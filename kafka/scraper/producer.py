#!/usr/bin/env python3
"""
Simple scraper producer:
- Loads kafka/config/whitelist.json
- Fetches homepages and discovers a few internal links
- Extracts title + paragraph text (basic)
- Produces JSON messages to Kafka topic

Notes:
- Development starter only. Add robots.txt checks, rate-limiting, site-specific parsers, sitemaps/RSS for production.
- Place a .env at repo root from kafka/.env.example
"""

import os
import json
from urllib.parse import urlparse, urljoin
from datetime import datetime
from time import sleep

import requests
from bs4 import BeautifulSoup
from kafka import KafkaProducer
from dotenv import load_dotenv
from tqdm import tqdm

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, '..', '.env'), override=False)

KAFKA_BOOTSTRAP = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = os.getenv('KAFKA_TOPIC', 'medical-articles')
USER_AGENT = os.getenv('SCRAPER_USER_AGENT', 'servvia-scraper/1.0')
MIN_TEXT_LENGTH = int(os.getenv('SCRAPER_MIN_TEXT_LENGTH', '300'))
WHITELIST_PATH = os.path.join(BASE_DIR, '..', 'config', 'whitelist.json')

HEADERS = {"User-Agent": USER_AGENT}

def load_whitelist(path=WHITELIST_PATH):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def fetch(url, timeout=15):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.text
    except Exception as e:
        print(f"[fetch] {url} -> {e}")
        return None

def extract_text(html):
    soup = BeautifulSoup(html, 'lxml')
    article = soup.find('article')
    if article:
        paras = article.find_all('p')
    else:
        main = soup.find('main') or soup.find('body')
        paras = main.find_all('p') if main else soup.find_all('p')
    text = ' '.join(p.get_text(separator=' ', strip=True) for p in paras)
    title_tag = soup.find('title')
    title = title_tag.get_text(strip=True) if title_tag else ''
    text = ' '.join(text.split())
    return title, text

def discover_links(html, base_url, max_links=8):
    soup = BeautifulSoup(html, 'lxml')
    parsed = urlparse(base_url)
    domain = parsed.netloc
    links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        full = urljoin(base_url, href)
        p = urlparse(full)
        if p.scheme.startswith('http') and domain in p.netloc and len(p.path) > 1:
            links.append(full)
            if len(links) >= max_links:
                break
    return list(dict.fromkeys(links))

def create_producer():
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP.split(','),
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        retries=5
    )

def build_msg(url, title, text, source):
    return {
        "url": url,
        "title": title,
        "text": text,
        "source": source,
        "scraped_at": datetime.utcnow().isoformat() + "Z"
    }

def scrape_and_produce():
    whitelist = load_whitelist()
    producer = create_producer()
    for entry in whitelist:
        domain = entry.get('domain')
        base_url = f"https://{domain}"
        print(f"[scrape] {domain}")
        home_html = fetch(base_url)
        if not home_html:
            print(f"[scrape] could not fetch {base_url}")
            continue
        candidates = [base_url] + discover_links(home_html, base_url, max_links=6)
        for url in tqdm(candidates, desc=domain, leave=False):
            html = fetch(url)
            if not html:
                continue
            title, text = extract_text(html)
            if not text or len(text) < MIN_TEXT_LENGTH:
                continue
            msg = build_msg(url, title, text, domain)
            producer.send(KAFKA_TOPIC, msg)
            producer.flush()
            print(f"[produce] {url} -> sent ({len(text)} chars)")
            sleep(0.5)
    producer.close()
    print("[scrape] finished")

if __name__ == "__main__":
    scrape_and_produce()