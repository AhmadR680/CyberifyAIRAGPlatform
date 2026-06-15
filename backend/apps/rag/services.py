from openai import OpenAI
from django.conf import settings
from django.db import models
from pgvector.django import CosineDistance
from .models import DocumentChunk
import uuid

# We will use OpenAI for embeddings since it's installed
try:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
except:
    client = None

def generate_embedding(text: str, provider="openai"):
    if provider == "gemini":
        from google import genai
        genai_client = genai.Client(api_key=settings.GEMINI_API_KEY)
        response = genai_client.models.embed_content(
            model='gemini-embedding-2',
            contents=text,
        )
        embedding = response.embeddings[0].values
        if len(embedding) > 1536:
            embedding = embedding[:1536]
        elif len(embedding) < 1536:
            embedding.extend([0.0] * (1536 - len(embedding)))
        return embedding
    else:
        if not client:
            return [0.0] * 1536
        try:
            response = client.embeddings.create(
                input=[text],
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            print("OpenAI Embedding Error:", e)
            return [0.0] * 1536

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def process_document_for_rag(document):
    if not document.extracted_text:
        return

    text = document.extracted_text
    chunks = chunk_text(text)
    
    # Clear existing chunks
    DocumentChunk.objects.filter(document=document).delete()

    for chunk in chunks:
        embedding = generate_embedding(chunk, provider=document.workspace.llm_provider)
        DocumentChunk.objects.create(
            document=document,
            text=chunk,
            embedding=embedding
        )

def search_documents(workspace, query: str, limit: int = 5):
    query_embedding = generate_embedding(query, provider=workspace.llm_provider)
    # Using pgvector distance operator: <-> for L2 distance, <=> for cosine distance
    # We will sort by cosine distance (<=)
    chunks = DocumentChunk.objects.filter(
        document__workspace=workspace
    ).order_by(
        CosineDistance('embedding', query_embedding)
    )[:limit]
    
    return [
        {"document_id": c.document.id, "filename": c.document.filename, "text": c.text}
        for c in chunks
    ]
