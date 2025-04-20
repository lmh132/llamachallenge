from database import Base

from sqlalchemy import (
    Column, String, Text, ForeignKey, DateTime, Enum as SQLEnum, Integer, CheckConstraint,
    func
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

# User model
class Test(Base):  
    __tablename__ = 'test'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), nullable=False)
class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    hashed_password = Column(String(128), nullable=False)

    # Relationships
    graphs = relationship('KnowledgeGraph', back_populates='owner', cascade='all, delete-orphan')
    knowledge = relationship('UserKnowledge', back_populates='user', cascade='all, delete-orphan')


class KnowledgeGraph(Base):
    __tablename__ = 'knowledge_graphs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    owner = relationship('User', back_populates='graphs')
    topics = relationship('Topic', back_populates='graph', cascade='all, delete-orphan')
    uploads = relationship('Upload', back_populates='graph', cascade='all, delete-orphan')


class Topic(Base):
    __tablename__ = 'topics'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    graph_id = Column(UUID(as_uuid=True), ForeignKey('knowledge_graphs.id'), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text)

    # Relationships
    graph = relationship('KnowledgeGraph', back_populates='topics')
    outgoing = relationship(
        'TopicConnection', foreign_keys='TopicConnection.from_topic_id',
        back_populates='from_topic', cascade='all, delete-orphan'
    )
    incoming = relationship(
        'TopicConnection', foreign_keys='TopicConnection.to_topic_id',
        back_populates='to_topic', cascade='all, delete-orphan'
    )
    user_knowledge = relationship('UserKnowledge', back_populates='topic', cascade='all, delete-orphan')


class TopicConnection(Base):
    __tablename__ = 'topic_connections'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    from_topic_id = Column(UUID(as_uuid=True), ForeignKey('topics.id'), nullable=False)
    to_topic_id = Column(UUID(as_uuid=True), ForeignKey('topics.id'), nullable=False)

    # Relationships
    from_topic = relationship('Topic', foreign_keys=[from_topic_id], back_populates='outgoing')
    to_topic = relationship('Topic', foreign_keys=[to_topic_id], back_populates='incoming')


class UserKnowledge(Base):
    __tablename__ = 'user_knowledge'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id'), nullable=False)
    topic_id = Column(UUID(as_uuid=True), ForeignKey('topics.id'), nullable=False)
    status = Column(
        Integer,
        CheckConstraint('status >= 1 AND status <= 100', name='status_range'),
        nullable=False,
        default=1
    )
    # Relationships
    user = relationship('User', back_populates='knowledge')
    topic = relationship('Topic', back_populates='user_knowledge')


class Upload(Base):
    __tablename__ = 'uploads'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(100), nullable=False)
    description = Column(Text)
    tag = Column(String(50))
    graph_id = Column(UUID(as_uuid=True), ForeignKey('knowledge_graphs.id'), nullable=False)
    file_path = Column(String(255), nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    graph = relationship('KnowledgeGraph', back_populates='uploads')
