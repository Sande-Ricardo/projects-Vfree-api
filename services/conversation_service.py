from db.client import get_supabase

async def get_or_create_conversation(project_id:str) -> str:
    supabase = get_supabase()
    
    existing = supabase.table('conversations').select('id').eq('project_id', project_id).order("created_at", desc=True).limit(1).execute()
    
    if existing.data:
        return existing.data[0]['id']
    
    new_con = supabase.table('conversations').insert({'project_id': project_id}).execute()
    
    return new_con.data[0]['id']

async def get_history(conversation_id:str, limit:int = 10) -> list:
    supabase = get_supabase()
    
    response = supabase.table("messages").select("role, content").eq("conversation_id", conversation_id).order("created_at", desc=True).limit(limit).execute()
    
    messages = list(reversed(response.data))
    
    return[{"rolr": m["role"], "content": m["content"]} for m in messages]

async def save_messages(conversation_id:str, project_id:str, question:str, answer:str) -> None:
    supabase = get_supabase()
    
    supabase.table("messages").insert([
        {
            "conversation_id": conversation_id,
            "project_id": project_id,
            "role": "user",
            "content": question
        },
        {
            "conversation_id": conversation_id,
            "project_id": project_id,
            "role": "assistant",
            "content": answer
        }
    ]).execute()
    
async def get_memory(project_id:str) -> list:
    supabase = get_supabase()
    
    response = supabase.table("memories").select("key, value").eq("project_id", project_id).execute()
    
    return response.data