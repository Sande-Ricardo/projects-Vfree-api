from config import settings
from openai import OpenAI

groq_client = OpenAI(
    api_key=settings.groq_api_key,
    base_url=settings.groq_base_url
)

def build_prompt(
    question:str,
    chunks:list,
    instructions:str = "",
    memory:list = []
) -> list:
    context_parts = []
    for i, chunk in enumerate(chunks):
        context_parts.append(
            f"[Fragment {i+1}]\n"
            f"Content: {chunk['content']}\n"
            )
    context = "\n---\n".join(context_parts)
    
    memory_text = ""
    if memory:
        memory_lines = "\n".join(f"-{m['key']}:{m['value']}" for m in memory)
        memory_text = f"\nKNOWN USER INFORMATION:\n{memory_lines}\n"
    
    system_content = instructions if instructions else (
        "You are a helpful assistant. "
        "Answer using only the information in the provided documentation fragments. "
        "If the answer is not in the fragments, say you so explicitly. "
        "Cite fragment umbers using [Fragment N]"
    )
    
    if memory_text:
        system_content += memory_text
        
    if context_parts:
        system_content += f"\n\nDOCUMENTATION FRAGMENTS:\n{context}\n"

    return [
        {"role": "system", "content": system_content},
        {"role": "user", "content": question}
    ]

async def generate_response(
    question:str,
    chunks:list,
    history:list = [],
    instructions:str = "",
    memory:list = []
) -> dict:
    if not chunks and not history:
        return {
            "answer": "No relevant information found.",
            "sources": []
            }
        
    messages = build_prompt(
        question,
        chunks,
        instructions,
        memory
    )
    
    if history:
        messages = [messages[0]] + history + messages[-1:]
    
    response = groq_client.chat.completions.create(
        model=settings.llm_model,
        messages=messages,
        temperature=0.3,
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