import json
from openai import OpenAI
from db.client import get_supabase
from config import settings

groq_client = OpenAI(
    api_key=settings.groq_api_key,
    base_url=settings.groq_base_url
)

EXTRACTION_PROMPT = """Your task is to extract relevant personal facts from the user message below.

Return ONLY a JSON array. Each element must have exactly two fields: "key" and "value".
- "key": short identifier in lowercase (examples: "name", "age", "role", "language_preference")
- "value": the extracted value as a string

Rules:
- Extract only concrete, reusable facts about the user (name, age, role, preferences, constraints).
- Do NOT extract questions, opinions, or temporary context.
- If there are no relevant facts, return an empty array: []
- Return ONLY the JSON array, no explanation, no markdown, no extra text.

Examples:
User: "Hi, I'm Boris, I'm 28 years old and I work as a backend developer"
Response: [{"key": "name", "value": "Boris"}, {"key": "age", "value": "28"}, {"key": "role", "value": "backend developer"}]

User: "What does this function do?"
Response: []

User: "Always answer in Spanish and keep responses under 5 sentences"
Response: [{"key": "language_preference", "value": "Spanish"}, {"key": "response_length", "value": "max 5 sentences"}]
"""

async def extract_and_save_memory(project_id:str, user_message:str) -> list:
    facts = await _extract_facts(user_message)
    
    if not facts:
        return []
    
    await _upsert_memories(project_id, facts)
    return facts

async def _extract_facts(user_message:str)-> list:
    try:
        response = groq_client.chat.completions.create(
            model=settings.llm_model,
            messages=[
                {"role": "system", "content":EXTRACTION_PROMPT},
                {"role": "user", "content":user_message}
            ],
            temperature=0.0, #REVIEW   - it could generate nothing -
            max_tokens=300
        )
        
        raw = response.choices[0].message.content.strip()
        
        if raw.startswith("```"):
            raw  = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
                
        facts = json.loads(raw)
        
        if not isinstance(facts, list):
            return []
        
        return [
            f for f in facts
            if isinstance(f, dict) and "key" in f and "value" in f
        ]
        
    except (json.JSONDecodeError, Exception):
        return []
    
    
async def _upsert_memories(project_id, facts:list) -> None:
    supabase = get_supabase()
    
    records = [
        {
            "project_id": project_id,
            "key": fact["key"],
            "value":fact["value"],
            "updated_at":"now()"
        }
        for fact in facts
    ]
    
    supabase.table("memories").upsert(
        records,
        on_conflict="project_id,key"
    ).execute()