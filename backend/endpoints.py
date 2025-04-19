from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from backend.database import SessionLocal
from backend.models import User, KnowledgeGraph, Topic, TopicConnection, UserKnowledge, Upload
from backend.auth import authenticate_user, create_access_token, get_current_user, hash_password
from backend.ocr import run_ocr
from backend.llm import extract_concepts, generate_quiz, refine_graph

# Dependency to get DB session
def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session

# Routers
auth_router = APIRouter(prefix="/auth", tags=["auth"])
upload_router = APIRouter(prefix="/upload", tags=["upload"])
graph_router = APIRouter(prefix="/graphs", tags=["graphs"])

# 5.1 Auth
@auth_router.post("/register")
async def register(username: str, email: str, password: str, db: AsyncSession = Depends(get_db)):
    # check existing
    if await db.execute(User.__table__.select().where(User.email==email)).first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
    user = User(username=username, email=email, hashed_password=hash_password(password))
    db.add(user); await db.commit(); await db.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email}

@auth_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

@auth_router.get("/me")
async def me(current_user: User = Depends(get_current_user)):
    return {"id": current_user.id, "username": current_user.username, "email": current_user.email}

# 5.2 File Upload & OCR
@upload_router.post("/", status_code=status.HTTP_201_CREATED)
async def upload_file(file: UploadFile = File(...), current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    path = f"uploads/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())
    text = await run_ocr(path)
    upload = Upload(graph_id=None, file_path=path, ocr_text=text)
    db.add(upload); await db.commit(); await db.refresh(upload)
    return {"id": upload.id, "file_path": upload.file_path, "ocr_text": upload.ocr_text, "uploaded_at": upload.uploaded_at}

@upload_router.get("/{upload_id}")
async def get_upload(upload_id: UUID, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    upload = await db.get(Upload, upload_id)
    if not upload:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    return {"id": upload.id, "file_path": upload.file_path, "ocr_text": upload.ocr_text, "uploaded_at": upload.uploaded_at}

# 5.3 Graph Management
@graph_router.post("/", status_code=status.HTTP_201_CREATED)
async def create_graph(upload_id: UUID, name: str, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # use LLM to extract and create
    upload = await db.get(Upload, upload_id)
    if not upload:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    concepts = await extract_concepts(upload.ocr_text)
    graph = KnowledgeGraph(user_id=current.id, name=name)
    db.add(graph); await db.commit(); await db.refresh(graph)
    # create Topic and Connection based on concepts
    for t in concepts['topics']:
        topic = Topic(graph_id=graph.id, name=t['name'], description=t.get('description'))
        db.add(topic)
    await db.commit()
    # ... similarly create TopicConnection
    return {"id": graph.id, "name": graph.name, "created_at": graph.created_at, "updated_at": graph.updated_at}

@graph_router.get("/")
async def list_graphs(current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(KnowledgeGraph.__table__.select().where(KnowledgeGraph.user_id==current.id))
    graphs = result.scalars().all()
    return [{"id": g.id, "name": g.name, "created_at": g.created_at, "updated_at": g.updated_at} for g in graphs]

@graph_router.get("/{graph_id}")
async def get_graph(graph_id: UUID, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    graph = await db.get(KnowledgeGraph, graph_id)
    if not graph or graph.user_id != current.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    nodes = [{"id": t.id, "name": t.name, "description": t.description} for t in graph.topics]
    edges = []
    for t in graph.topics:
        for conn in t.outgoing:
            edges.append({"id": conn.id, "from": conn.from_topic_id, "to": conn.to_topic_id})
    return {"nodes": nodes, "edges": edges}

@graph_router.delete("/{graph_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_graph(graph_id: UUID, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    graph = await db.get(KnowledgeGraph, graph_id)
    if not graph or graph.user_id != current.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    await db.delete(graph); await db.commit()

# 5.4 Node & Connection
@graph_router.get("/{graph_id}/nodes/")
async def list_nodes(graph_id: UUID, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    return (await get_graph(graph_id, current, db))["nodes"]

@graph_router.get("/{graph_id}/nodes/{node_id}")
async def node_detail(graph_id: UUID, node_id: UUID, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    topic = await db.get(Topic, node_id)
    if not topic or topic.graph_id != graph_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    prereq = [ {"id": c.from_topic.id, "name": c.from_topic.name} for c in topic.incoming ]
    summary = topic.description  # or call LLM summary
    return {"id": topic.id, "name": topic.name, "description": topic.description, "prerequisites": prereq, "summary": summary}

@graph_router.get("/{graph_id}/edges/")
async def list_edges(graph_id: UUID, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    graph = await db.get(KnowledgeGraph, graph_id)
    if not graph or graph.user_id != current.id:
        raise HTTPException(status.HTTP_404_NOT_FOUND)
    edges = []
    for t in graph.topics:
        for conn in t.outgoing:
            edges.append({"id": conn.id, "from": conn.from_topic_id, "to": conn.to_topic_id})
    return edges

# 5.5 Assessment & Refinement
@graph_router.post("/{graph_id}/assess")
async def assess(graph_id: UUID, answers: dict, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    # answers: {question_id: answer}
    results = await generate_quiz(graph_id, answers)
    return {"results": results}

@graph_router.post("/{graph_id}/refine")
async def refine(graph_id: UUID, current: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    updated = await refine_graph(graph_id)
    return {"updated_graph": updated}
