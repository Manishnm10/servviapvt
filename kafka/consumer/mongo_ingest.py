#!/usr/bin/env python3
"""
Kafka consumer -> MongoDB ingest

- Consume messages from Kafka topic
- Basic validation
- Compute embedding with sentence-transformers
- Upsert into existing MongoDB collection (use same DB as FarmStack/servviapvt)

Notes:
- For production, consider content hashing dedupe, chunking, bulk writes, and using Atlas Vector Search or FAISS for ANN.
"""

import os
import json
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from kafka import KafkaConsumer
from sentence_transformers import SentenceTransformer
from pymongo import MongoClient
from pymongo.errors import PyMongoError

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '..', '.env'), override=False)

# Kafka
KAFKA_BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'medical-articles')
KAFKA_GROUP = os.getenv('KAFKA_GROUP_ID', 'medical-ingest-group')

# Mongo
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017')
MONGO_DB = os.getenv('MONGO_DB', 'servviapvt')
MONGO_COLLECTION = os.getenv('MONGO_COLLECTION', 'medical_articles')

# Embedding model
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
MIN_TEXT_LEN = int(os.getenv('SCRAPER_MIN_TEXT_LENGTH', '300'))

print(f"[ingest] loading model {EMBEDDING_MODEL}")
model = SentenceTransformer(EMBEDDING_MODEL)
vec_dim = model.get_sentence_embedding_dimension()
print(f"[ingest] model loaded (dim={vec_dim})")

# Mongo client
mongo = MongoClient(MONGO_URI)
db = mongo[MONGO_DB]
collection = db[MONGO_COLLECTION]

def validate_message(msg):
    required = ['url', 'title', 'text', 'source', 'scraped_at']
    for k in required:
        if k not in msg:
            return False, f"missing {k}"
    if not isinstance(msg['text'], str) or len(msg['text']) < MIN_TEXT_LEN:
        return False, f"text too short ({len(msg.get('text') or '')})"
    return True, None

def content_hash(text):
    h = hashlib.sha256()
    h.update(text.encode('utf-8'))
    return h.hexdigest()

def upsert_to_mongo(msg, embedding):
    now = datetime.utcnow().isoformat() + "Z"
    doc = {
        "url": msg['url'],
        "title": msg.get('title'),
        "text": msg.get('text'),
        "source": msg.get('source'),
        "scraped_at": msg.get('scraped_at'),
        "ingested_at": now,
        "embedding": embedding,
        "content_hash": content_hash(msg.get('text', ''))
    }
    try:
        res = collection.update_one(
            {"url": msg['url']},
            {"$set": doc, "$setOnInsert": {"_created_at": now}},
            upsert=True
        )
        return True
    except PyMongoError as e:
        print(f"[mongo] upsert error: {e}")
        return False

def consume_and_ingest():
    consumer = KafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP.split(','),
        group_id=KAFKA_GROUP,
        value_deserializer=lambda v: json.loads(v.decode('utf-8')),
        auto_offset_reset='earliest',
        enable_auto_commit=True
    )
    print(f"[kafka] listening to {KAFKA_TOPIC} on {KAFKA_BOOTSTRAP} ...")
    for record in consumer:
        try:
            msg = record.value
            valid, reason = validate_message(msg)
            if not valid:
                print(f"[validate] skip: {reason}")
                continue
            text = msg['text']
            emb = model.encode(text).tolist()
            ok = upsert_to_mongo(msg, emb)
            if ok:
                print(f"[ingest] upserted {msg.get('url')}")
            else:
                print(f"[ingest] failed to upsert {msg.get('url')}")
        except Exception as e:
            print(f"[ingest] error: {e}")

if __name__ == "__main__":
    consume_and_ingest()