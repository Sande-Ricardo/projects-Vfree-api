import os
from google import genai
from dotenv import load_dotenv

load_dotenv()
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

response = client.models.embed_content(
    model="models/gemini-embedding-001",
    contents="embedding test"
)

print(f"Dimensions: {len(response.embeddings[0].values)}")