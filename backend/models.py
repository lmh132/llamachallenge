from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from backend.database import Base

class Topic(Base):
    __tablename__ = 'topics'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)

    # Connections from this topic to others (prerequisites for other topics)
    prerequisites_for = relationship(
        'TopicConnection',
        foreign_keys='TopicConnection.from_topic_id',
        back_populates='from_topic',
        cascade='all, delete-orphan'
    )

    # Connections pointing to this topic (topics required before learning this)
    prerequisites_needed = relationship(
        'TopicConnection',
        foreign_keys='TopicConnection.to_topic_id',
        back_populates='to_topic',
        cascade='all, delete-orphan'
    )
class TopicConnection(Base):
    __tablename__ = 'topic_connections'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Topic you must learn first (prerequisite)
    from_topic_id = Column(UUID(as_uuid=True), ForeignKey('topics.id'), nullable=False)
    
    # Topic you learn next
    to_topic_id = Column(UUID(as_uuid=True), ForeignKey('topics.id'), nullable=False)

    # Relationship to topics
    from_topic = relationship('Topic', foreign_keys=[from_topic_id], back_populates='prerequisites_for')
    to_topic = relationship('Topic', foreign_keys=[to_topic_id], back_populates='prerequisites_needed')
    
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)