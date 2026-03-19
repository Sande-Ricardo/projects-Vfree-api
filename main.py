from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.ingest import router as ingest_router
from routers.query import router as query_router
from routers.documents import router as documents_router

app = FastAPI()

app.title = "Recall API"
app.description = "API for technical docs assistant with RAG"
app.version = "0.1.0"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(ingest_router)
app.include_router(query_router)
app.include_router(documents_router)

@app.get("/", tags=["Root"])
async def root():
    return {"message":"Root Page"}

@app.get("/health", tags=["Health"])
async def health():
    return {"status":"ok-"}

