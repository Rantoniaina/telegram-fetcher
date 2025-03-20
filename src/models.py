from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

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
    media_path = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_normalized = Column(Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"<Message(id={self.id}, message_id={self.message_id})>"


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