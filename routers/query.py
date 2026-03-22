from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from services.retrieval_service import retrieve_chunks
from services.llm_service import generate_response
from db.client import get_supabase
from services.conversation_service import get_or_create_conversation, save_messages, get_history, get_memory

router = APIRouter(prefix="/query", tags=["query"])

class QueryRequest(BaseModel):
    project_id:str
    question:str
    top_k:int = None
    
@router.post("/")
async def query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    
    supabase = get_supabase()
    project = supabase.table("projects").select("id, instructions").eq("id", request.project_id).single().execute()
    
    if not project.data:
        raise HTTPException(status_code=404, detail="Project not found.")
    
    instructions = project.data.get("instructions", "")
    
    conversation_id = await get_or_create_conversation(request.project_id)
    
    chunks, history, memory = await _gather_context(
        question = request.project_id,
        conversation_id = conversation_id,
        project_id = request.project_id,
        top_k = request.top_k)
    
    result = await generate_response(
        question=request.question,
        chunks = chunks,
        history = history,
        instructions = instructions,
        memory = memory
    )
    
    await save_messages(
        conversation_id = conversation_id,
        project_id = request.project_id,
        question = request.question,
        answer = result["answer"]
    )
        
    return {
        "question": request.question,
        "answer": result["answer"],
        "sources": result["sources"],
        "conversation_id": conversation_id
    }
    
    
@router.delete("/{project_id}/history", status_code=204)
async def clear_history(project_id:str):

    supabase = get_supabase()
    supabase.table("conversations").delete().eq("project_id", project_id).execute()
    
async def _gather_context(
    question: str,
    project_id: str,
    conversation_id: str,
    top_k: int
) -> tuple:
    chunks = await retrieve_chunks(question, project_id, top_k)
    history = await get_history(conversation_id)
    memory = await get_memory(project_id)
    
    return chunks, history, memory
    