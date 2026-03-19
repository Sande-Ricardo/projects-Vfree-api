from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
    
    groq_api_key: str
    groq_base_url: str
    
    gemini_api_key: str
    
    supabase_url: str
    supabase_service_key: str
    
    chunk_size: int = 800
    chunk_overlap: int = 200
    top_k: int = 5
    similarity_threshold: float = 0.3
    
    llm_model: str = "llama-3.3-70b-versatile"
    embedding_model: str = "models/gemini-embedding-001"
    embedding_dimensions: int = 3072
    
        

settings = Settings()

