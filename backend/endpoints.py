from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from backend.database import SessionLocal
from backend.models import User, KnowledgeGraph, Topic, TopicConnection, UserKnowledge, Upload
from backend.auth import hash_password, authenticate_user, create_access_token
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

# 5.1 Auth Endpoints remain unchanged
@auth_router.post("/register")
async def register(username: str, email: str, password: str, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(User.__table__.select().where(User.email == email))
    if existing.first():
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email already registered")
    user = User(username=username, email=email, hashed_password=hash_password(password))
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email}

@auth_router.post("/login")
async def login(username: str, password: str, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, username, password)
    if not user:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    token = create_access_token({"sub": str(user.id)})
    return {"access_token": token, "token_type": "bearer"}

# 5.2 File Upload & OCR for specific user_id
@upload_router.post("/{user_id}", status_code=status.HTTP_201_CREATED)
async def upload_file_for_user(
    user_id: UUID,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    # Save file and run OCR
    path = f"uploads/{file.filename}"
    with open(path, "wb") as f:
        f.write(await file.read())
    text = await run_ocr(path)
    upload = Upload(graph_id=None, file_path=path, ocr_text=text)
    db.add(upload)
    await db.commit()
    await db.refresh(upload)
    return {"id": upload.id, "file_path": upload.file_path, "ocr_text": upload.ocr_text, "uploaded_at": upload.uploaded_at}

@upload_router.get("/{user_id}/{upload_id}")
async def get_upload_for_user(
    user_id: UUID,
    upload_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    upload = await db.get(Upload, upload_id)
    if not upload:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Upload not found")
    return {"id": upload.id, "file_path": upload.file_path, "ocr_text": upload.ocr_text, "uploaded_at": upload.uploaded_at}

# 5.3 Graph Management for specific user_id
@graph_router.post("/{user_id}", status_code=status.HTTP_201_CREATED)
async def create_graph_for_user(
    user_id: UUID,
    upload_id: UUID,
    name: str,
    db: AsyncSession = Depends(get_db)
):
    upload = await db.get(Upload, upload_id)
    if not upload:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Upload not found")
    concepts = await extract_concepts(upload.ocr_text)
    graph = KnowledgeGraph(user_id=user_id, name=name)
    db.add(graph)
    await db.commit()
    await db.refresh(graph)
    # Create Topic and TopicConnection entries per concepts
    for t in concepts.get('topics', []):
        topic = Topic(graph_id=graph.id, name=t['name'], description=t.get('description'))
        db.add(topic)
    await db.commit()
    return {"id": graph.id, "name": graph.name, "created_at": graph.created_at, "updated_at": graph.updated_at}

@graph_router.get("/{user_id}")
async def list_graphs_for_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        KnowledgeGraph.__table__.select().where(KnowledgeGraph.user_id == user_id)
    )
    graphs = result.scalars().all()
    return [
        {"id": g.id, "name": g.name, "created_at": g.created_at, "updated_at": g.updated_at}
        for g in graphs
    ]

@graph_router.get("/{user_id}/{graph_id}")
async def get_graph_for_user(
    user_id: UUID,
    graph_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    graph = await db.get(KnowledgeGraph, graph_id)
    if not graph or graph.user_id != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Graph not found")
    nodes = [
        {"id": t.id, "name": t.name, "description": t.description}
        for t in graph.topics
    ]
    edges = []
    for t in graph.topics:
        for conn in t.outgoing:
            edges.append({"id": conn.id, "from": conn.from_topic_id, "to": conn.to_topic_id})
    return {"nodes": nodes, "edges": edges}

@graph_router.delete("/{user_id}/{graph_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_graph_for_user(
    user_id: UUID,
    graph_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    graph = await db.get(KnowledgeGraph, graph_id)
    if not graph or graph.user_id != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Graph not found")
    await db.delete(graph)
    await db.commit()

# 5.4 Node & Connection retrieval for specific user_id and graph
@graph_router.get("/{user_id}/{graph_id}/nodes/")
async def list_nodes_for_user(
    user_id: UUID,
    graph_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    graph = await db.get(KnowledgeGraph, graph_id)
    if not graph or graph.user_id != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Graph not found")
    return [
        {"id": t.id, "name": t.name, "description": t.description}
        for t in graph.topics
    ]

@graph_router.get("/{user_id}/{graph_id}/nodes/{node_id}")
async def node_detail_for_user(
    user_id: UUID,
    graph_id: UUID,
    node_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    topic = await db.get(Topic, node_id)
    if not topic or topic.graph_id != graph_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Node not found")
    prereqs = [
        {"id": c.from_topic.id, "name": c.from_topic.name}
        for c in topic.incoming
    ]
    summary = topic.description
    return {"id": topic.id, "name": topic.name, "description": topic.description, "prerequisites": prereqs, "summary": summary}

@graph_router.get("/{user_id}/{graph_id}/edges/")
async def list_edges_for_user(
    user_id: UUID,
    graph_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    graph = await db.get(KnowledgeGraph, graph_id)
    if not graph or graph.user_id != user_id:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Graph not found")
    edges = []
    for t in graph.topics:
        for conn in t.outgoing:
            edges.append({"id": conn.id, "from": conn.from_topic_id, "to": conn.to_topic_id})
    return edges

# 5.5 Assessment & Refinement for specific user_id
@graph_router.post("/{user_id}/{graph_id}/assess")
async def assess_for_user(
    user_id: UUID,
    graph_id: UUID,
    answers: dict,
    db: AsyncSession = Depends(get_db)
):
    results = await generate_quiz(graph_id, answers)
    return {"results": results}

@graph_router.post("/{user_id}/{graph_id}/refine")
async def refine_for_user(
    user_id: UUID,
    graph_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    updated = await refine_graph(graph_id)
    return {"updated_graph": updated}
