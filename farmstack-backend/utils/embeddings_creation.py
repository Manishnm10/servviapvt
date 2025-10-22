import logging
import os
import tempfile
import argparse
import concurrent.futures
import csv
import json
import re
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import contextmanager
from urllib.parse import quote_plus
from uuid import UUID

import certifi
import openai
import pytube
import pytz
import requests
from bs4 import BeautifulSoup
from django.db import models
from django.db.models import OuterRef, Subquery
from django.db.models.functions import Cast
from docx import Document

from dotenv import load_dotenv

from langchain_community.document_loaders import (
    BSHTMLLoader, CSVLoader, JSONLoader, PyMuPDFLoader, UnstructuredHTMLLoader
)
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores.pgvector import DistanceStrategy
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from pgvector.django import CosineDistance, L2Distance
from psycopg.conninfo import make_conninfo
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph, SimpleDocTemplate

from requests import Request, Session
from requests.adapters import HTTPAdapter
from sqlalchemy.dialects.postgresql import dialect
from urllib3.util import Retry

from celery import shared_task
from core import settings
from core.constants import Constants
from datahub.models import LangchainPgCollection, LangchainPgEmbedding, OutputParser, ResourceFile
from utils.chain_builder import ChainBuilder
from langchain.prompts import PromptTemplate
from utils.pgvector import PGVector
from langchain.retrievers.merger_retriever import MergerRetriever

from langchain.retrievers import (
    ContextualCompressionRetriever,
    MergerRetriever,
)
from langchain.retrievers.document_compressors import DocumentCompressorPipeline

from langchain_community.document_transformers import (
    EmbeddingsClusteringFilter,
    EmbeddingsRedundantFilter,
)
from langchain_core.output_parsers import JsonOutputParser

LOGGING = logging.getLogger(__name__)

load_dotenv()
os.environ["OPENAI_API_KEY"] = settings.OPENAI_API_KEY
openai.api_key = settings.OPENAI_API_KEY

embedding_model = "text-embedding-ada-002"
embeddings = OpenAIEmbeddings(model=embedding_model, openai_api_key=settings.OPENAI_API_KEY)

db_settings = settings.DATABASES['default']
encoded_user = quote_plus(db_settings['USER'])
encoded_password = quote_plus(db_settings['PASSWORD'])
retriever = ''

connectionString = f"postgresql://{encoded_user}:{encoded_password}@{db_settings['HOST']}:{db_settings['PORT']}/{db_settings['NAME']}"

def load_vector_db(resource_id, filters):
    embeddings = OpenAIEmbeddings(model=embedding_model, openai_api_key=settings.OPENAI_API_KEY)

    LOGGING.info("Looking into resource: {resource_id} embeddings")
    collection_ids = LangchainPgCollection.objects.filter(
        name__in=Subquery(
            ResourceFile.objects.filter(resource=resource_id)
            .annotate(string_id=Cast('id', output_field=models.CharField()))
            .values('string_id')
        )
    ).values_list('uuid', flat=True)
    vector_db = PGVector(
        collection_name="ALL",
        connection_string=connectionString,
        embedding_function=embeddings,
    )
    retriever = vector_db.as_retriever(search_args={'k': 5}, search_type="similarity_score_threshold", search_kwargs={"filter": filters, "score_threshold": 0.8})
    return retriever, vector_db

    embeddings = OpenAIEmbeddings(model=embedding_model, openai_api_key=settings.OPENAI_API_KEY)

    def setup_retriever(collection_id):
        vector_db = PGVector(
            collection_name=str(collection_id),
            connection_string=connectionString,
            embedding_function=embeddings,
        )
        retriever = vector_db.as_retriever(search_type="similarity", search_args={'k': 5})
        return retriever
    retrievals = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_collection_id = {executor.submit(setup_retriever, collection_id): collection_id for collection_id in collection_ids}
        for future in as_completed(future_to_collection_id):
            collection_id = future_to_collection_id[future]
            try:
                retriever = future.result()
                retrievals.append(retriever)
            except Exception as exc:
                LOGGING.error(f'{collection_id} generated an exception: {exc}')

    merge_retriever = MergerRetriever(retrievers=retrievals)
    filter = EmbeddingsRedundantFilter(embeddings=embeddings)
    pipeline = DocumentCompressorPipeline(transformers=[filter])
    compression_retriever = ContextualCompressionRetriever(
        base_compressor=pipeline, base_retriever=merge_retriever)
    a = compression_retriever.similarity_search_with_score("Tell me about wheat varities")
    return compression_retriever

def transcribe_audio(audio_bytes, language="en-US"):
    try:
        transcript = openai.Audio.translate(file=audio_bytes, model="whisper-1")
        return transcript
    except Exception as e:
        print("Transcription error:", str(e))
        return str(e)

class VectorBuilder:
    # ... rest is unchanged ...
    # [For brevity, include the unchanged class implementation from your file]

    # When you instantiate OpenAIEmbeddings anywhere else in this file, do it like:
    # embeddings = OpenAIEmbeddings(model=embedding_model, openai_api_key=settings.OPENAI_API_KEY)

# The rest of your file remains unchanged except:
# - Update all `OpenAIEmbeddings()` calls to: `OpenAIEmbeddings(model=embedding_model, openai_api_key=settings.OPENAI_API_KEY)`
# - All `langchain.document_loaders` imports replaced with `langchain_community.document_loaders`