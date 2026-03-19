from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.ingest_service import ingest_document

router = APIRouter()

@router.post("/ingest", tags=["Ingest"])
async def ingest(
    file: UploadFile = File(...),
    title: str = Form(...)
):
    allowed_types = ["pdf", "txt", "md"]
    file_type = file.filename.split(".")[-1].lower()
    
    if file_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file_type}. Allowed types are: {', '.join(allowed_types)}"
        )
        
    file_content = await file.read()
    result = await ingest_document(file_content, file.filename, title)
    return result