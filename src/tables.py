import sqlalchemy as sa
import uuid

metadata = sa.MetaData()
engine = sa.create_engine("sqlite:///./test.db", connect_args={"check_same_thread": False})
conn = engine.connect()


user_table = sa.Table(
    "users",
    metadata,
    sa.Column("id", sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    sa.Column("username", sa.String(50), unique=True, nullable=False),
    sa.Column("email", sa.String(120), unique=True, nullable=False),
    sa.Column("hashed_password", sa.String(128), nullable=False),
)

knowledge_graph_table = sa.Table(
    "knowledge_graphs",
    metadata,
    sa.Column("id", sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("name", sa.String(100), nullable=False),
    sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now(), nullable=False),
)

topic_table = sa.Table(
    "topics",
    metadata,
    sa.Column("id", sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    sa.Column("graph_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("name", sa.String(100), nullable=False),
    sa.Column("description", sa.Text),
)

topic_connection_table = sa.Table(
    "topic_connections",
    metadata,
    sa.Column("id", sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    sa.Column("graph_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("from_topic_id", sa.String(36), sa.ForeignKey("topics.id"), nullable=False),
    sa.Column("to_topic_id", sa.String(36), sa.ForeignKey("topics.id"), nullable=False),
)

user_knowledge_table = sa.Table(
    "user_knowledge",
    metadata,
    sa.Column("id", sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    sa.Column("user_id", sa.String(36), sa.ForeignKey("users.id"), nullable=False),
    sa.Column("topic_id", sa.String(36), sa.ForeignKey("topics.id"), nullable=False),
    sa.Column("status", sa.Integer, sa.CheckConstraint('status >= 1 AND status <= 100'), nullable=False, default=1),
)

upload_table = sa.Table(
    "uploads",
    metadata,
    sa.Column("id", sa.String(36), primary_key=True, default=lambda: str(uuid.uuid4())),
    sa.Column("graph_id", sa.String(36), sa.ForeignKey("knowledge_graphs.id"), nullable=False),
    sa.Column("file_path", sa.String(255), nullable=False),
    sa.Column("ocr_text", sa.Text),
    sa.Column("uploaded_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
)

metadata.create_all(engine)