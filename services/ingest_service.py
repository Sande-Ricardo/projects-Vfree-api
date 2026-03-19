# backend/services/ingest_service.py
import os
import tempfile
from google import genai
from db.client import get_supabase
from utils.loaders import get_loader
from utils.splitter import get_splitter
from config import settings

gemini_client = genai.Client(api_key=settings.gemini_api_key)

async def ingest_document(file_content: bytes, file_name: str, title: str, project_id) -> dict:
    file_type = file_name.split(".")[-1].lower()
    supabase = get_supabase()

    doc_response = supabase.table("documents").insert({
        "project_id": project_id,
        "title": title,
        "file_name": file_name,
        "file_type": file_type,
        "file_size": len(file_content),
        "status": "processing"
    }).execute()

    document_id = doc_response.data[0]["id"]

    try:
        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=f".{file_type}"
        ) as tmp:
            tmp.write(file_content)
            tmp_path = tmp.name

        loader = get_loader(tmp_path, file_type)
        documents = loader.load()
        splitter = get_splitter()
        chunks = splitter.split_documents(documents)

        chunk_records = []
        for index, chunk in enumerate(chunks):
            response = gemini_client.models.embed_content(
                model=settings.embedding_model,
                contents=chunk.page_content,
            )
            embedding = response.embeddings[0].value

            chunk_records.append({
                "document_id": document_id,
                "project_id": project_id,
                "content": chunk.page_content,
                "embedding": embedding,
                "chunk_index": index,
                "metadata": chunk.metadata
            })

        supabase.table("chunks").insert(chunk_records).execute()

        supabase.table("documents").update(
            {"status": "ready"}
        ).eq("id", document_id).execute()

        return {
            "document_id": document_id,
            "chunk_count": len(chunks),
            "status": "ready"
        }

    except Exception as e:
        supabase.table("documents").update(
            {"status": "error"}
        ).eq("id", document_id).execute()
        raise e

    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)