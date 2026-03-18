"""
SQLAlchemy ORM models — SQLite compatible.
UUIDs stored as TEXT. JSON stored as TEXT (serialized).
"""
from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy import String, Integer, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db.session import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


class Document(Base):
    __tablename__ = "documents"

    id:          Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    title:       Mapped[str] = mapped_column(Text, nullable=False)
    doc_type:    Mapped[str] = mapped_column(String(20), nullable=False, default="unknown")
    year:        Mapped[int | None] = mapped_column(Integer, nullable=True)
    subject:     Mapped[str | None] = mapped_column(Text, nullable=True)
    filename:    Mapped[str] = mapped_column(Text, nullable=False)
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    blocks:    list[Block]    = relationship("Block",    back_populates="document", cascade="all, delete")
    questions: list[Question] = relationship("Question", back_populates="document", cascade="all, delete")


class Block(Base):
    __tablename__ = "blocks"

    id:           Mapped[str] = mapped_column(String, primary_key=True, default=new_uuid)
    doc_id:       Mapped[str] = mapped_column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    block_type:   Mapped[str] = mapped_column(String(20), nullable=False)
    page:         Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    content:      Mapped[str] = mapped_column(Text, nullable=False)   # JSON serialized
    embedding_id: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at:   Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    document: Document = relationship("Document", back_populates="blocks")


class Question(Base):
    __tablename__ = "questions"

    id:               Mapped[str]   = mapped_column(String, primary_key=True, default=new_uuid)
    doc_id:           Mapped[str]   = mapped_column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    text:             Mapped[str]   = mapped_column(Text, nullable=False)
    topic:            Mapped[str | None] = mapped_column(Text, nullable=True)
    year:             Mapped[int | None] = mapped_column(Integer, nullable=True)
    prediction_score: Mapped[float] = mapped_column(Float, default=0.0)
    last_scored_at:   Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    document: Document = relationship("Document", back_populates="questions")