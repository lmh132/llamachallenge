from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from llama_stack_client import Agent, AgentEventLogger, RAGDocument, LlamaStackClient
from llama_stack_client.types import Model
import re
import json
import pdfplumber
import io

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
tutor_agent, decomp_agent = None, None
tutor_session_id, decomp_session_id = None, None

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

def create_agents():
    global tutor_agent, decomp_agent

    decomp_agent = Agent(
        client,
        model=llm_model.identifier,
        instructions="""You are a foundational topic decomposition engine.

        Given a complex topic, break it down into a hierarchy of prerequisite subtopics that must be understood in order to fully grasp the final topic.

        Return the result as a **JSON object**, where:

        - Each **key** is a prerequisite topic (something you must learn first).
        - Each **value** is the topic that **depends on the key**.
        - The **final queried topic** is the root and should have `"ROOT"` as its parent.
        - The hierarchy should build **bottom-up**, from the most basic concepts to the root topic.

        ### Output Format

        {
        "<Foundational Concept>": "<Next Topic That Builds On It>",
        ...
        "<Queried Topic>": "ROOT"
        }

        ### Example:

        Main Topic: Machine Learning

        Output:
        {
        "Basic Statistics and Probability": "Linear Algebra and Calculus",
        "Linear Algebra and Calculus": "Supervised Learning",
        "Supervised Learning": "Regression and Classification",
        "Regression and Classification": "Neural Networks",
        "Neural Networks": "Deep Learning Applications",
        "Deep Learning Applications": "Machine Learning",
        "Machine Learning": "ROOT"
        }

        Make sure the topics you create are not too broad or too narrow. They should be specific enough to be meaningful, but not so specific that they are useless. For example "Electromagnetism" is too broad, while "The Lorentz Force Law" is too narrow. A good topic might be "Electromagnetic Waves".
        Avoid using overly technical jargon or abbreviations that a layperson might not understand. Use clear, simple language to describe each topic.

        Return only a valid JSON object with double quotes around all keys and values. Do not include any explanation, code block markers (like ```), or extra text. The JSON should be directly parsable by `json.loads()`.

        ### Now do the same for:

        Main Topic: {{YOUR_TOPIC_HERE}}
        """,
        tools=[
            {
                "name": "builtin::rag/knowledge_search",
                "args": {"vector_db_ids": [VECTOR_DB_ID]},
            }
        ],
    )

    tutor_agent = Agent(
        client,
        model=llm_model.identifier,
        instructions="""YYou are an expert tutor engine designed to teach complex topics to learners in a clear, structured, and approachable way.

        When given a topic, your job is to break it down into well-organized parts, with each part covering a distinct concept or step in understanding the topic.

        Your explanation should include:
        - Clear definitions
        - Step-by-step reasoning or derivation (if mathematical or technical)
        - Examples or analogies
        - References to prerequisite or related topics
        - A summary or conclusion that ties the concepts together

        ### Output Format:

        Topic: <TOPIC>

        1. Introduction  
        - What is the topic?  
        - Why is it important?  
        - Where is it used?

        2. Core Concepts  
        - List and explain each key concept clearly  
        - Link to any related or prerequisite ideas  
        - Use visuals or analogies if helpful

        3. Derivation / Reasoning (if applicable)  
        - Walk through the steps logically  
        - Define variables  
        - Explain each step in simple terms

        4. Examples  
        - Provide 1–2 relevant examples  
        - Show how the concepts apply

        5. Related Topics  
        - What topics should be learned before/after this one?

        6. Summary  
        - Recap what was learned  
        - Reinforce why it's important

        ### Now explain the following topic using the above structure:

        <TOPIC>: {{YOUR_TOPIC_HERE}}
        """,
        tools=[
            {
                "name": "builtin::rag/knowledge_search",
                "args": {"vector_db_ids": [VECTOR_DB_ID]},
            }
        ],
    )

def create_sessions():
    global tutor_session_id, decomp_session_id
    tutor_session_id = tutor_agent.create_session(SESSION_NAME)
    decomp_session_id = decomp_agent.create_session(SESSION_NAME)

# --- Run Setup on Startup ---
@app.on_event("startup")
def startup():
    initialize_models()
    setup_vector_db()
    #ingest_document()
    create_agents()
    create_sessions()

# --- Request Schema ---
class ChatRequest(BaseModel):
    user_id: str
    prompt: str

# --- /chat Streaming Endpoint ---
@app.post("/tutorchat")
def chat(request: ChatRequest):
    response = tutor_agent.create_turn(
        messages=[{"role": "user", "content": request.prompt}],
        session_id=tutor_session_id,
        stream=True,
    )

    output = ""
    for log in AgentEventLogger().log(response):
        if log.role == "inference":
            continue
        #print(vars(log))
        output += str(log)

    return {"response": output.strip()}

@app.post("/decomp")
def chat(request: ChatRequest):
    response = decomp_agent.create_turn(
        messages=[{"role": "user", "content": request.prompt}],
        session_id=decomp_session_id,
        stream=True,
    )

    output = ""
    for log in AgentEventLogger().log(response):
        #print(vars(log))
        if log.role == "inference":
            continue
        output += str(log)

    try:
        parsed = json.loads(output)
        return {"data": parsed}
    except json.JSONDecodeError:
        return {"error": "Could not parse response as JSON", "raw": output}
    

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    contents = await file.read()
    extracted_text = extract_text_from_pdf(contents)
    prompt = f"Summarize this:\n{extracted_text}"

    response = tutor_agent.create_turn(
        messages=[{"role": "user", "content": prompt}],
        session_id=tutor_session_id,
        stream=True,
    )

    def stream():
        for log in AgentEventLogger().log(response):
            yield str(log).strip()

    return StreamingResponse(stream(), media_type="text/plain")

