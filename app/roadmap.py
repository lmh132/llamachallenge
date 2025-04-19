# app/roadmap.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict
from collections import defaultdict

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from backend.database import SessionLocal
from backend.models import Topic, TopicConnection

router = APIRouter()


### Pydantic schemas for the LLM response ###
class TopicCreate(BaseModel):
    name: str
    description: Optional[str] = None

class ConnectionCreate(BaseModel):
    from_topic: str
    to_topic: str

class LLMResponse(BaseModel):
    topics: List[TopicCreate]
    connections: List[ConnectionCreate]


### Dependency to get a DB session ###
async def get_db() -> AsyncSession:
    async with SessionLocal() as session:
        yield session


@router.post("/topics/import", summary="Import topics + connections from LLM output")
async def import_topics(
    payload: LLMResponse,
    db: AsyncSession = Depends(get_db),
):
    # 1) Upsert all topics, keep a map name→Topic
    topic_map: Dict[str, Topic] = {}
    for t in payload.topics:
        q = await db.execute(select(Topic).where(Topic.name == t.name))
        topic = q.scalar_one_or_none()
        if not topic:
            topic = Topic(name=t.name, description=t.description)
            db.add(topic)
            await db.flush()      # so .id is populated
        topic_map[t.name] = topic

    await db.commit()

    # 2) Create TopicConnection edges
    for c in payload.connections:
        src = topic_map.get(c.from_topic)
        dst = topic_map.get(c.to_topic)
        if not src or not dst:
            continue  # skip if a topic was missing
        # check for existing edge
        q = await db.execute(
            select(TopicConnection)
            .where(TopicConnection.from_topic_id == src.id)
            .where(TopicConnection.to_topic_id == dst.id)
        )
        if not q.scalar_one_or_none():
            edge = TopicConnection(
                from_topic_id=src.id,
                to_topic_id=dst.id
            )
            db.add(edge)

    await db.commit()
    return {"imported_topics": len(topic_map), "imported_connections": len(payload.connections)}


@router.get("/roadmap", summary="List all prerequisite paths from start→target")
async def get_roadmap(
    start: str,
    target: str,
    db: AsyncSession = Depends(get_db),
):
    # 1) Load start/target topics
    q = await db.execute(select(Topic).where(Topic.name == start))
    start_topic = q.scalar_one_or_none()
    if not start_topic:
        raise HTTPException(404, f"Start topic '{start}' not found")

    q = await db.execute(select(Topic).where(Topic.name == target))
    target_topic = q.scalar_one_or_none()
    if not target_topic:
        raise HTTPException(404, f"Target topic '{target}' not found")

    # 2) Preload all Topic.id→name
    q = await db.execute(select(Topic.id, Topic.name))
    rows = q.all()  # list of (id, name)
    id_to_name = {rid: name for rid, name in rows}

    # 3) Build adjacency list from from_topic_id → list of to_topic_id
    q = await db.execute(select(TopicConnection.from_topic_id, TopicConnection.to_topic_id))
    conns = q.all()
    adj: Dict[str, List[str]] = defaultdict(list)
    for src_id, dst_id in conns:
        adj[src_id].append(dst_id)

    # 4) DFS to collect all paths from start_topic.id → target_topic.id
    all_paths: List[List[int]] = []
    def dfs(node_id: str, path: List[str]):
        path.append(node_id)
        if node_id == target_topic.id:
            all_paths.append(path.copy())
        else:
            for nbr in adj.get(node_id, []):
                if nbr not in path:        # avoid cycles
                    dfs(nbr, path)
        path.pop()

    dfs(start_topic.id, [])

    # 5) Convert ID paths → name paths
    name_paths = [
        [id_to_name[nid] for nid in path]
        for path in all_paths
    ]

    return {"paths": name_paths}
