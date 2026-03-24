from fastapi import APIRouter, HTTPException
from db.client import get_supabase

router = APIRouter(prefix="/documents", tags=["Documents"])

@router.get("/")
async def list_documents(project_id:str):
    supabase = get_supabase()
    
    result = supabase.table("documents").select("id, title, file_name, file_type, file_size, status, created_at").eq("project_id", project_id).order("created_at", desc = True).execute()
    return result.data
# async def get_documents():
#     supabase = get_supabase()
    
#     result = supabase.table("documents").select("*").order(
#         "created_at",
#         desc=True
#     ).execute()
    
#     documents = []
#     for doc in result.data:
#         chunks_result = supabase.table("chunks").select(
#             "id", count="exact"
#         ).eq("document_id",doc["id"]).execute()
        
#         documents.append({
#             **doc,
#             "chunk_count": chunks_result.count
#         })
    
#     return {"documents": documents}


@router.delete("/{document_id}")
async def delete_document(document_id:str):
    supabase = get_supabase()
    
    result = supabase.table("documents").select("id").eq(
        "id", document_id
    ).execute()

    if result.count == 0:
        raise HTTPException(status_code=404, detail="Document not found")

    supabase.table("chunks").delete().eq(
        "document_id", document_id
    ).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Document not found")

    supabase.table("documents").delete().eq(
        "id", document_id
    ).execute()

    return {"deleted": True}
