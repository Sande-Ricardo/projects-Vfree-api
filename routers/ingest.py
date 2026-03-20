from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.ingest_service import ingest_document
from db.client import get_supabase

router = APIRouter(prefix="/ingest", tags=["Ingest"])

@router.post("")
async def ingest(
    file: UploadFile = File(...),
    title: str = Form(...),
    project_id: str = Form(...)
):
    supabase = get_supabase()
    project = supabase.table("projects").select("*").eq("id", project_id).single().execute()
    if not project.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
    allowed_types = ["pdf", "txt", "md"]
    file_type = file.filename.split(".")[-1].lower()
    
    if file_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_type}. Allowed types are: {', '.join(allowed_types)}"
        )
        
    file_content = await file.read()
    result = await ingest_document(
        file_content = file_content,
        file_name = file.filename,
        title = title,
        project_id = project_id
    )
    return result