from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, create_engine, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from .config import settings

Base = declarative_base()


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, unique=True, nullable=False)
    date = Column(DateTime, nullable=False)
    chat_id = Column(Integer, nullable=False)
    sender_id = Column(Integer)
    text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_normalized = Column(Boolean, default=False, nullable=False)

    # Relationship to media files
    media_files = relationship("MediaFile", back_populates="message")

    def __repr__(self):
        return f"<Message(id={self.id}, message_id={self.message_id})>"


class MediaFile(Base):
    __tablename__ = "media_files"

    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String)  # To store the type of media (photo, video, document, etc.)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship to message
    message = relationship("Message", back_populates="media_files")

    def __repr__(self):
        return f"<MediaFile(id={self.id}, message_id={self.message_id}, file_type={self.file_type})>"


class NormalizedMessage(Base):
    __tablename__ = "normalized_messages"

    id = Column(Integer, primary_key=True)
    original_message_id = Column(Integer, ForeignKey('messages.id'), nullable=False)
    normalized_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship to original message
    original_message = relationship("Message", backref="normalized_version")

    def __repr__(self):
        return f"<NormalizedMessage(id={self.id}, original_message_id={self.original_message_id})>"


# Database setup
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()