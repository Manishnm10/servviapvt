```markdown
# kafka/ (ingest) — Scraper + Kafka -> MongoDB

This directory contains a simple development pipeline to scrape trusted medical sources, publish article JSONs to Kafka, and ingest (with embeddings) into your existing MongoDB used by servviapvt.

Recommended layout
- kafka/docker-compose.yml
- kafka/.env.example
- kafka/requirements.txt
- kafka/config/whitelist.json
- kafka/scraper/producer.py
- kafka/consumer/mongo_ingest.py

Quickstart (local dev)
1. Copy .env.example to a .env at the repo root and set values (MONGO_URI should point to your servviapvt DB).
2. Start Kafka:
   docker-compose -f kafka/docker-compose.yml up -d
3. Install Python deps:
   python -m venv venv
   source venv/bin/activate
   pip install -r kafka/requirements.txt
4. Run the producer (scrapes whitelist, publishes to Kafka):
   python kafka/scraper/producer.py
5. Run the consumer (ingests into Mongo):
   python kafka/consumer/mongo_ingest.py

Notes & recommended improvements
- Respect robots.txt, rate limits, and target sites' terms of use.
- Prefer sitemaps/RSS or official APIs for high-quality ingestion.
- Add language detection, more rigorous validation, and canonicalization/deduplication.
- For production vector search, use MongoDB Atlas Vector Search or run FAISS/hnswlib as a separate ANN service.
- Use bulk upserts for throughput when ingesting large volumes.

Placement recommendation
- Keep kafka/ as a top-level folder so it is decoupled from servvia runtime. If later you want deep integration, convert the consumer to a Django management command that imports project settings.

Security
- Add /kafka/.env to .gitignore
- Do not commit credentials in .env
```