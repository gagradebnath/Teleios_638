"""
db/models.py — SQLAlchemy 2.x ORM models.
All primary keys are TEXT (UUID strings).
JSON content stored as TEXT (serialized by the service layer).
Timestamps stored as TEXT in ISO format (SQLite has no native datetime type).
"""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, Integer, Float, Text, ForeignKey, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base


def _new_uuid() -> str:
    return str(uuid.uuid4())


# ── Document ──────────────────────────────────────────────────────────────────

class Document(Base):
    """
    Represents an ingested PDF — either a textbook or a past exam paper.
    One document has many Blocks (extracted content) and many Questions.
    """
    __tablename__ = "documents"

    id:          Mapped[str]           = mapped_column(String,     primary_key=True, default=_new_uuid)
    title:       Mapped[str]           = mapped_column(Text,       nullable=False)
    doc_type:    Mapped[str]           = mapped_column(String(20), nullable=False, default="unknown")
    year:        Mapped[Optional[int]] = mapped_column(Integer,    nullable=True)
    subject:     Mapped[Optional[str]] = mapped_column(Text,       nullable=True)
    filename:    Mapped[str]           = mapped_column(Text,       nullable=False)
    uploaded_at: Mapped[datetime]      = mapped_column(DateTime,   default=datetime.utcnow, nullable=False)

    blocks:    Mapped[list["Block"]]    = relationship("Block",    back_populates="document", cascade="all, delete-orphan")
    questions: Mapped[list["Question"]] = relationship("Question", back_populates="document", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Document id={self.id!r} title={self.title!r} type={self.doc_type!r}>"


# ── Block ─────────────────────────────────────────────────────────────────────

class Block(Base):
    """
    A single parsed block from a document page.
    block_type: 'text' | 'equation' | 'figure' | 'table'
    content: JSON string — schema varies by block_type (see gateway/schemas.py).
    embedding_id: the ChromaDB vector ID for this block (set after indexing).
    """
    __tablename__ = "blocks"

    id:           Mapped[str]           = mapped_column(String,     primary_key=True, default=_new_uuid)
    doc_id:       Mapped[str]           = mapped_column(String,     ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    block_type:   Mapped[str]           = mapped_column(String(20), nullable=False, default="text")
    page:         Mapped[int]           = mapped_column(Integer,    nullable=False, default=0)
    content:      Mapped[str]           = mapped_column(Text,       nullable=False)   # JSON
    embedding_id: Mapped[Optional[str]] = mapped_column(Text,       nullable=True)
    created_at:   Mapped[datetime]      = mapped_column(DateTime,   default=datetime.utcnow, nullable=False)

    document: Mapped["Document"] = relationship("Document", back_populates="blocks")

    def __repr__(self) -> str:
        return f"<Block id={self.id!r} type={self.block_type!r} page={self.page}>"


# ── Question ──────────────────────────────────────────────────────────────────

class Question(Base):
    """
    An exam question extracted from a past paper.
    prediction_score is computed by PredictionAgent and updated in place.
    Questions are NEVER fabricated — only extracted from ingested documents.
    """
    __tablename__ = "questions"

    id:               Mapped[str]            = mapped_column(String,  primary_key=True, default=_new_uuid)
    doc_id:           Mapped[str]            = mapped_column(String,  ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    text:             Mapped[str]            = mapped_column(Text,    nullable=False)
    topic:            Mapped[Optional[str]]  = mapped_column(Text,    nullable=True)
    year:             Mapped[Optional[int]]  = mapped_column(Integer, nullable=True)
    prediction_score: Mapped[float]          = mapped_column(Float,   nullable=False, default=0.0)
    last_scored_at:   Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    document: Mapped["Document"] = relationship("Document", back_populates="questions")

    def __repr__(self) -> str:
        return f"<Question id={self.id!r} topic={self.topic!r} score={self.prediction_score:.3f}>"