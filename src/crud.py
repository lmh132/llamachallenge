import uuid
from sqlalchemy import insert, select, update, delete
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
from tables import (
    user_table, knowledge_graph_table, topic_table,
    topic_connection_table, user_knowledge_table, upload_table
)

# --- User CRUD ---
def create_user(engine: Engine, username: str, email: str, hashed_password: str):
    user_id = str(uuid.uuid4())
    stmt = insert(user_table).values(
        id=user_id,
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    return user_id


def get_user_by_username(engine: Engine, username: str):
    stmt = select(user_table).where(user_table.c.username == username)
    with engine.connect() as conn:
        result = conn.execute(stmt).fetchone()
    return dict(result) if result else None

# --- Knowledge Graph CRUD ---
def create_graph(engine: Engine, user_id: str, name: str):
    graph_id = str(uuid.uuid4())
    stmt = insert(knowledge_graph_table).values(
        id=graph_id,
        user_id=user_id,
        name=name
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    return graph_id


def get_graphs_by_user(engine: Engine, user_id: str):
    stmt = select(knowledge_graph_table).where(knowledge_graph_table.c.user_id == user_id)
    with engine.connect() as conn:
        return [dict(row) for row in conn.execute(stmt).fetchall()]

# --- Topic CRUD ---
def create_topic(engine: Engine, graph_id: str, name: str, description: str = ""):
    topic_id = str(uuid.uuid4())
    stmt = insert(topic_table).values(
        id=topic_id,
        graph_id=graph_id,
        name=name,
        description=description
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    return topic_id


def get_topics_by_graph(engine: Engine, graph_id: str):
    stmt = select(topic_table).where(topic_table.c.graph_id == graph_id)
    with engine.connect() as conn:
        return [dict(row) for row in conn.execute(stmt).fetchall()]

# --- Topic Connections ---
def create_topic_connection(engine: Engine, from_topic_id: str, to_topic_id: str):
    conn_id = str(uuid.uuid4())
    stmt = insert(topic_connection_table).values(
        id=conn_id,
        from_topic_id=from_topic_id,
        to_topic_id=to_topic_id
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    return conn_id

# --- User Knowledge ---
def track_user_knowledge(engine: Engine, user_id: str, topic_id: str, status: int = 1):
    knowledge_id = str(uuid.uuid4())
    stmt = insert(user_knowledge_table).values(
        id=knowledge_id,
        user_id=user_id,
        topic_id=topic_id,
        status=status
    )
    with engine.begin() as conn:
        conn.execute(stmt)
    return knowledge_id


def get_user_knowledge(engine: Engine, user_id: str):
    stmt = select(user_knowledge_table).where(user_knowledge_table.c.user_id == user_id)
    with engine.connect() as conn:
        return [dict(row) for row in conn.execute(stmt).fetchall()]
