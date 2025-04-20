import uuid
from sqlalchemy import insert, select, update, delete
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError
import sqlalchemy as sa
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

# --- Topic Hierarchy ---
def create_topic_hierarchy(engine: Engine, graph_id: str, topic_dict: dict):
    """Creates topics and their connections from a dictionary of prerequisite -> dependent topics"""
    topic_ids = {}
    
    with engine.begin() as conn:
        # Create topics
        for prereq_topic, dependent_topic in topic_dict.items():
            # Create prerequisite topic if it doesn't exist
            if prereq_topic not in topic_ids:
                stmt = select(topic_table).where(topic_table.c.name == prereq_topic)
                topic = conn.execute(stmt).first()
                if not topic:
                    topic_id = str(uuid.uuid4())
                    stmt = insert(topic_table).values(
                        id=topic_id,
                        graph_id=graph_id,  # Changed from user_id to graph_id
                        name=prereq_topic,
                        description=None
                    )
                    conn.execute(stmt)
                    topic_ids[prereq_topic] = topic_id
                else:
                    topic_ids[prereq_topic] = topic.id

            # Create dependent topic if it doesn't exist and isn't "ROOT"
            if dependent_topic != "ROOT" and dependent_topic not in topic_ids:
                stmt = select(topic_table).where(topic_table.c.name == dependent_topic)
                topic = conn.execute(stmt).first()
                if not topic:
                    topic_id = str(uuid.uuid4())
                    stmt = insert(topic_table).values(
                        id=topic_id,
                        graph_id=graph_id,  # Changed from user_id to graph_id
                        name=dependent_topic,
                        description=None
                    )
                    conn.execute(stmt)
                    topic_ids[dependent_topic] = topic_id
                else:
                    topic_ids[dependent_topic] = topic.id

        # Create connections
        for prereq_topic, dependent_topic in topic_dict.items():
            if dependent_topic != "ROOT":
                stmt = select(topic_connection_table).where(
                    sa.and_(
                        topic_connection_table.c.from_topic_id == topic_ids[prereq_topic],
                        topic_connection_table.c.to_topic_id == topic_ids[dependent_topic]
                    )
                )
                if not conn.execute(stmt).first():
                    stmt = insert(topic_connection_table).values(
                        id=str(uuid.uuid4()),
                        graph_id=graph_id,  # Changed from user_id to graph_id
                        from_topic_id=topic_ids[prereq_topic],
                        to_topic_id=topic_ids[dependent_topic]
                    )
                    conn.execute(stmt)

    return topic_ids

def get_graph_by_id(engine: Engine, graph_id: str):
    """
    Retrieves all topics and their connections for a given graph.
    Returns a dictionary with 'nodes' and 'edges' lists.
    """
    # Get all topics (nodes) for the graph
    topics_stmt = select(
        topic_table.c.id,
        topic_table.c.name,
        topic_table.c.description,
        topic_table.c.graph_id
    ).where(topic_table.c.graph_id == graph_id)
    
    # Get all connections (edges) for the graph
    connections_stmt = select(
        topic_connection_table.c.id,
        topic_connection_table.c.from_topic_id,
        topic_connection_table.c.to_topic_id,
        topic_connection_table.c.graph_id
    ).where(topic_connection_table.c.graph_id == graph_id)
    
    with engine.connect() as conn:
        # Fetch nodes
        nodes = [
            {
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "graph_id": row.graph_id
            }
            for row in conn.execute(topics_stmt).fetchall()
        ]
        
        # Fetch edges
        edges = [
            {
                "id": row.id,
                "from_topic_id": row.from_topic_id,
                "to_topic_id": row.to_topic_id,
                "graph_id": row.graph_id
            }
            for row in conn.execute(connections_stmt).fetchall()
        ]
        
        return {
            "nodes": nodes,
            "edges": edges
        }

def get_user_knowledge_graph(engine: Engine, graph_id: str):
    """
    Retrieves all topics and their connections for a given graph.
    Returns a dictionary with 'nodes' and 'edges' lists.
    """
    # Get all topics (nodes) for the graph
    topics_stmt = select(topic_table).where(topic_table.c.graph_id == graph_id)
    
    # Get all connections (edges) for the graph
    connections_stmt = select(topic_connection_table).where(
        topic_connection_table.c.graph_id == graph_id
    )
    
    with engine.connect() as conn:
        # Fetch nodes
        topics_result = conn.execute(topics_stmt)
        nodes = [
            {
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "graph_id": row.graph_id
            }
            for row in topics_result.fetchall()
        ]
        
        # Fetch edges
        connections_result = conn.execute(connections_stmt)
        edges = [
            {
                "id": row.id,
                "from_topic_id": row.from_topic_id,
                "to_topic_id": row.to_topic_id,
                "graph_id": row.graph_id
            }
            for row in connections_result.fetchall()
        ]
        
        return {
            "nodes": nodes,
            "edges": edges
        }