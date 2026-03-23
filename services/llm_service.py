from config import settings
from openai import OpenAI

groq_client = OpenAI(
    api_key=settings.groq_api_key,
    base_url=settings.groq_base_url
)

def build_system_prompt(
    chunks:list,
    instructions:str = "",
    memory:list = []
) -> str:
    system_content = instructions if instructions else (
        "You are a helpful assistant. "
        "Answer using only the information in the provided documentation fragments. "
        "If the answer is not in the fragments, say so explicitly. "
        "Cite fragment numbers using [Fragment N]."
    )
    
    if memory:
        memory_lines = "\n".join(f"- {m['key']}: {m['value']}" for m in memory)
        system_content += f"\n\nKNOWN USER INFORMATION:\n{memory_lines}"
        
    if chunks:
        context_parts = []
        for i, chunk in enumerate(chunks):
            context_parts.append(
                f"[Fragment {i+1}]\n"
                f"Content: {chunk['content']}"
            )
        context = "\n---\n".join(context_parts)
        system_content += f"\n\nDOCUMENTATION FRAGMENTS:\n{context}"
    return system_content

async def generate_response(
    question:str,
    chunks:list,
    history:list = [],
    instructions: str = [],
    memory:list = []
) -> dict:
    if not chunks and not history:
        return {
            "answer": "No relevant information found",
            "sources":[]
        }
    system_prompt = build_system_prompt(chunks, instructions, memory)
    
    messages = (
        [{"role":"system", "content":system_prompt}]
        + history
        + [{"role":"user", "content":question}]
    )
    
    response = groq_client.chat.completions.create(
        model = settings.llm_model,
        messages= messages,
        temperature= 0.3,
    )
    
    sources = [
        {
            "chunk_id": chunk["id"],
            "content": chunk["content"],
            "section": chunk.get("section"),
            "document_id": chunk["document_id"],
            "similarity": round(chunk["similarity"], 4)
        }
        for chunk in chunks
    ]
    
    return {
        "answer": response.choices[0].message.content,
        "sources": sources
    }