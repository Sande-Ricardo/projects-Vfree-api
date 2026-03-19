from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.retrieval_service import retrieve_chunks
from services.llm_service import generate_response

router = APIRouter()

class QueryRequest(BaseModel):
    question:str
    top_k:int = None
    
@router.post("/query", tags=["Query"])
async def query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    chunks = await retrieve_chunks(request.question, request.top_k)
    
    result = await generate_response(request.question, chunks)
    
    if not chunks:
        return {
            "question": request.question,
            "chunks": [],
            "message": "No relevant chunks found."
        }
    
    return {
        "question": request.question,
        "answer": result["answer"],
        "sources": result["sources"]
    }