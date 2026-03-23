from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from db.client import get_supabase

router = APIRouter(prefix="/projects", tags=["projects"])

class ProjectCreate(BaseModel):
    title: str
    instructions: str
    
class ProjectUpdate(BaseModel):
    title: str | None = None
    instructions: str | None = None


@router.get("/")
async def lit_proects():
    supabase = get_supabase()
    response = supabase.table("projects").select("*").order("created_at", desc= True).execute()
    return response.data

@router.post("/", status_code=201)
async def create_project(body: ProjectCreate):
    supabase = get_supabase()
    response = supabase.table("projects").insert(
        {
            "title": body.title,
            "instructions": body.instructions
        }
    ).execute()
    return response.data

@router.get("/{project_id}")
async def get_project(project_id: str):
    supabase = get_supabase()
    response = supabase.table("projects").select("*").eq("id", project_id).single().execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Project not found")
    return response.data
    
@router.patch("/{project_id}")
async def update_project(project_id: str, body: ProjectUpdate):
    supabase = get_supabase()
    updates = body.model_dump(exclude_none=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")
    response = supabase.table("projects").update(updates).eq("id", project_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Project not found")
    return response.data[0]

@router.delete("/{project_id}", status_code=204)
async def delete_project(project_id: str):
    supabase = get_supabase()
    response = supabase.table("projects").delete().eq("id", project_id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Project not found")
    
@router.get("/{project_id}/memory")
async def get_project_memory(project_id: str):
    supabase = get_supabase()
    response = supabase.table("memories").select("key, value, updated_at").eq("project_id", project_id).order("updated_at", desc=True).execute()
    return response.data

@router.delete("/{project_id}/memory", status_code=204)
async def clear_project_memory(project_id:str):
    supabase = get_supabase()
    supabase.table("memories").delete().eq("project_id", project_id).execute()