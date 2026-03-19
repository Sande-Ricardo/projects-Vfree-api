from db.client import get_supabase
from config import settings
from google import genai

gemini_client = genai.Client(api_key=settings.gemini_api_key)

async def retrieve_chunks(question:str, project_id:str, top_k:int = None) -> list:
    k = top_k or settings.top_k
    
    response = gemini_client.models.embed_content(
        model= settings.embedding_model,
        contents= question
    )
    query_embedding = response.embeddings[0].value
    
    supabase = get_supabase()
    result = supabase.rpc('match_chunks', {
        "query_embedding": query_embedding,
        "match_project_id": project_id,
        "match_threshold": settings.similarity_threshold,
        "match_count": k
    }).execute()
    
    
    return result.data