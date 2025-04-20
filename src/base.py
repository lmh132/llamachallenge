from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from llama_stack_client import Agent, AgentEventLogger, RAGDocument, LlamaStackClient
from llama_stack_client.types import Model
import fitz  # PyMuPDF
import io
import pdfplumber
from fastapi import HTTPException
import aiohttp 

def extract_text_from_pdf(bytes_data: bytes) -> str:
    text = ""
    with pdfplumber.open(io.BytesIO(bytes_data)) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
            text += "\n"
    return text


# --- Constants ---
BASE_URL = "http://localhost:8321"
VECTOR_DB_ID = "my_demo_vector_db"
DOC_URL = "https://www.paulgraham.com/greatwork.html"
SESSION_NAME = "rag_session_pg"

# --- Global Setup ---
app = FastAPI()
client = LlamaStackClient(base_url=BASE_URL)

# One-time model and DB setup
llm_model = None
embedding_model = None
agent = None
session_id = None

# --- Setup Functions ---
def initialize_models():
    global llm_model, embedding_model
    models = client.models.list()
    llm_model = next(m for m in models if m.model_type == "llm")
    embedding_model = next(m for m in models if m.model_type == "embedding")

def setup_vector_db():
    client.vector_dbs.register(
        vector_db_id=VECTOR_DB_ID,
        embedding_model=embedding_model.identifier,
        embedding_dimension=embedding_model.metadata["embedding_dimension"],
        provider_id="faiss",
    )

def ingest_document():
    document = RAGDocument(
        document_id="document_pg",
        content=DOC_URL,
        mime_type="text/html",
        metadata={},
    )
    client.tool_runtime.rag_tool.insert(
        documents=[document],
        vector_db_id=VECTOR_DB_ID,
        chunk_size_in_tokens=50,
    )

def create_agent():
    global agent
    agent = Agent(
        client,
        model=llm_model.identifier,
        instructions="You are a helpful assistant.",
        tools=[
            {
                "name": "builtin::rag/knowledge_search",
                "args": {"vector_db_ids": [VECTOR_DB_ID]},
            }
        ],
    )

def create_session():
    global session_id
    session_id = agent.create_session(SESSION_NAME)

# --- Run Setup on Startup ---
@app.on_event("startup")
def startup():
    initialize_models()
    setup_vector_db()
    ingest_document()
    create_agent()
    create_session()

# --- Request Schema ---
class ChatRequest(BaseModel):
    user_id: str
    prompt: str

# --- /chat Streaming Endpoint ---
@app.post("/chat")
def chat(request: ChatRequest):
    response = agent.create_turn(
        messages=[{"role": "user", "content": request.prompt}],
        session_id=session_id,
        stream=True,
    )

    def stream():
        for log in AgentEventLogger().log(response):
            line = str(log).strip()
            yield line

    return StreamingResponse(stream(), media_type="text/plain")



@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(None),
    url: str = Form(None)
):
    if url:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        raise HTTPException(status_code=400, detail="Failed to fetch PDF from URL.")
                    contents = await resp.read()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error fetching URL: {str(e)}")
    elif file:
        contents = await file.read()
    else:
        raise HTTPException(status_code=400, detail="Either a file or a URL must be provided.")

    extracted_text = extract_text_from_pdf(contents)
    prompt = f"Summarize this:\n{extracted_text}"

    response = agent.create_turn(
        messages=[{"role": "user", "content": prompt}],
        session_id=session_id,
        stream=True,
    )

    def stream():
        for log in AgentEventLogger().log(response):
            yield str(log).strip()

    return StreamingResponse(stream(), media_type="text/plain")@app.post("/upload-pdf")

@app.post("/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(None),
    url: str = Form(None)
):
    if url:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status != 200:
                        raise HTTPException(status_code=400, detail="Failed to fetch PDF from URL.")
                    contents = await resp.read()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error fetching URL: {str(e)}")
    elif file:
        contents = await file.read()
    else:
        raise HTTPException(status_code=400, detail="Either a file or a URL must be provided.")

    extracted_text = extract_text_from_pdf(contents)
    prompt = f"Summarize this:\n{extracted_text}"

    response = agent.create_turn(
        messages=[{"role": "user", "content": prompt}],
        session_id=session_id,
        stream=True,
    )

    def stream():
        for log in AgentEventLogger().log(response):
            yield str(log).strip()

    return StreamingResponse(stream(), media_type="text/plain")