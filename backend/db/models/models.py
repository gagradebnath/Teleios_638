"""
db/models/models.py — SQLAlchemy 2.x ORM models.
All primary keys are TEXT (UUID strings).
JSON content stored as TEXT (serialized by the service layer).
Timestamps stored as TEXT in ISO 8601 format (SQLite has no native datetime type).

Enhanced schema includes:
- File system hierarchy (courses, file_system_nodes)
- Knowledge base (kb_items, kb_blocks, question_solution_pairs)
- Study tracking (study_sessions, explanations, conversation_history)
- Processing pipeline (document_pages, raw_extractions, processing_jobs)
- Topic analysis and importance scoring
"""
from __future__ import annotations
import uuid
from datetime import datetime, UTC
from typing import Optional

from sqlalchemy import String, Integer, Float, Text, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.session import Base


def _new_uuid() -> str:
    return str(uuid.uuid4())


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


# ── Course ───────────────────────────────────────────────────────────────────

class Course(Base):
    """Represents a course/subject for organizing study materials."""
    __tablename__ = "courses"

    id:          Mapped[str]           = mapped_column(String, primary_key=True, default=_new_uuid)
    name:        Mapped[str]           = mapped_column(Text, nullable=False)
    code:        Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    color:       Mapped[str]           = mapped_column(String(20), nullable=False, default="#3b82f6")
    created_at:  Mapped[str]           = mapped_column(String, nullable=False, default=_now_iso)
    updated_at:  Mapped[str]           = mapped_column(String, nullable=False, default=_now_iso)

    file_system_nodes: Mapped[list["FileSystemNode"]] = relationship("FileSystemNode", back_populates="course", cascade="all, delete-orphan")
    documents:         Mapped[list["Document"]]        = relationship("Document", back_populates="course")
    kb_items:          Mapped[list["KnowledgeBaseItem"]] = relationship("KnowledgeBaseItem", back_populates="course")
    study_sessions:    Mapped[list["StudySession"]]    = relationship("StudySession", back_populates="course", cascade="all, delete-orphan")
    topics:            Mapped[list["TopicAnalysis"]]   = relationship("TopicAnalysis", back_populates="course", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Course id={self.id!r} name={self.name!r}>"


# ── FileSystemNode ────────────────────────────────────────────────────────────

class FileSystemNode(Base):
    """Hierarchical file/folder structure like Google Drive."""
    __tablename__ = "file_system_nodes"

    id:         Mapped[str]           = mapped_column(String, primary_key=True, default=_new_uuid)
    parent_id:  Mapped[Optional[str]] = mapped_column(String, ForeignKey("file_system_nodes.id", ondelete="CASCADE"), nullable=True)
    course_id:  Mapped[Optional[str]] = mapped_column(String, ForeignKey("courses.id", ondelete="CASCADE"), nullable=True)
    name:       Mapped[str]           = mapped_column(Text, nullable=False)
    node_type:  Mapped[str]           = mapped_column(String(10), nullable=False, default="file")
    path:       Mapped[str]           = mapped_column(Text, nullable=False)
    size_bytes: Mapped[int]           = mapped_column(Integer, nullable=False, default=0)
    mime_type:  Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    created_at: Mapped[str]           = mapped_column(String, nullable=False, default=_now_iso)
    updated_at: Mapped[str]           = mapped_column(String, nullable=False, default=_now_iso)

    parent:   Mapped[Optional["FileSystemNode"]] = relationship("FileSystemNode", remote_side=[id], back_populates="children")
    children: Mapped[list["FileSystemNode"]]     = relationship("FileSystemNode", back_populates="parent", cascade="all, delete-orphan")
    course:   Mapped[Optional["Course"]]         = relationship("Course", back_populates="file_system_nodes")
    documents: Mapped[list["Document"]]          = relationship("Document", back_populates="file_system_node")

    def __repr__(self) -> str:
        return f"<FileSystemNode id={self.id!r} type={self.node_type!r} path={self.path!r}>"


# ── Document ──────────────────────────────────────────────────────────────────

class Document(Base):
    """
    Represents an ingested PDF — either a textbook or a past exam paper.
    One document has many Blocks (extracted content) and many Questions.
    Enhanced with course assignment, file system link, and processing status.
    """
    __tablename__ = "documents"

    id:                  Mapped[str]           = mapped_column(String,     primary_key=True, default=_new_uuid)
    title:               Mapped[str]           = mapped_column(Text,       nullable=False)
    doc_type:            Mapped[str]           = mapped_column(String(20), nullable=False, default="unknown")
    year:                Mapped[Optional[int]] = mapped_column(Integer,    nullable=True)
    subject:             Mapped[Optional[str]] = mapped_column(Text,       nullable=True)
    filename:            Mapped[str]           = mapped_column(Text,       nullable=False)
    uploaded_at:         Mapped[str]           = mapped_column(String,     nullable=False, default=_now_iso)
    
    # New columns
    course_id:           Mapped[Optional[str]] = mapped_column(String, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    file_system_node_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("file_system_nodes.id", ondelete="SET NULL"), nullable=True)
    processing_status:   Mapped[str]           = mapped_column(String(20), nullable=False, default="pending")
    total_pages:         Mapped[int]           = mapped_column(Integer, nullable=False, default=0)
    file_size_bytes:     Mapped[int]           = mapped_column(Integer, nullable=False, default=0)
    file_path:           Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata:            Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON

    blocks:              Mapped[list["Block"]]           = relationship("Block", back_populates="document", cascade="all, delete-orphan")
    questions:           Mapped[list["Question"]]        = relationship("Question", back_populates="document", cascade="all, delete-orphan")
    pages:               Mapped[list["DocumentPage"]]    = relationship("DocumentPage", back_populates="document", cascade="all, delete-orphan")
    raw_extractions:     Mapped[list["RawExtraction"]]   = relationship("RawExtraction", back_populates="document", cascade="all, delete-orphan")
    course:              Mapped[Optional["Course"]]      = relationship("Course", back_populates="documents")
    file_system_node:    Mapped[Optional["FileSystemNode"]] = relationship("FileSystemNode", back_populates="documents")
    study_sessions:      Mapped[list["StudySession"]]    = relationship("StudySession", back_populates="document")
    explanations:        Mapped[list["Explanation"]]     = relationship("Explanation", back_populates="document")

    def __repr__(self) -> str:
        return f"<Document id={self.id!r} title={self.title!r} type={self.doc_type!r}>"


# ── DocumentPage ──────────────────────────────────────────────────────────────

class DocumentPage(Base):
    """Page-level metadata for documents."""
    __tablename__ = "document_pages"

    id:          Mapped[str]            = mapped_column(String, primary_key=True, default=_new_uuid)
    doc_id:      Mapped[str]            = mapped_column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number: Mapped[int]            = mapped_column(Integer, nullable=False)
    width:       Mapped[Optional[float]]= mapped_column(Float, nullable=True)
    height:      Mapped[Optional[float]]= mapped_column(Float, nullable=True)
    has_text:    Mapped[bool]           = mapped_column(Boolean, nullable=False, default=True)
    has_images:  Mapped[bool]           = mapped_column(Boolean, nullable=False, default=False)
    has_math:    Mapped[bool]           = mapped_column(Boolean, nullable=False, default=False)
    thumbnail:   Mapped[Optional[str]]  = mapped_column(Text, nullable=True)  # Base64
    processed:   Mapped[bool]           = mapped_column(Boolean, nullable=False, default=False)
    created_at:  Mapped[str]            = mapped_column(String, nullable=False, default=_now_iso)

    document: Mapped["Document"] = relationship("Document", back_populates="pages")

    def __repr__(self) -> str:
        return f"<DocumentPage doc_id={self.doc_id!r} page={self.page_number}>"


# ── RawExtraction ─────────────────────────────────────────────────────────────

class RawExtraction(Base):
    """Temporary storage for raw OCR output before LLM cleaning."""
    __tablename__ = "raw_extractions"

    id:                  Mapped[str]           = mapped_column(String, primary_key=True, default=_new_uuid)
    doc_id:              Mapped[str]           = mapped_column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    page_number:         Mapped[int]           = mapped_column(Integer, nullable=False)
    raw_text:            Mapped[str]           = mapped_column(Text, nullable=False)
    extraction_metadata: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    created_at:          Mapped[str]           = mapped_column(String, nullable=False, default=_now_iso)
    processed:           Mapped[bool]          = mapped_column(Boolean, nullable=False, default=False)

    document: Mapped["Document"] = relationship("Document", back_populates="raw_extractions")

    def __repr__(self) -> str:
        return f"<RawExtraction doc_id={self.doc_id!r} page={self.page_number}>"


# ── Block ─────────────────────────────────────────────────────────────────────

class Block(Base):
    """
    A single parsed block from a document page.
    block_type: 'text' | 'equation' | 'figure' | 'table'
    content: JSON string — schema varies by block_type (see gateway/schemas.py).
    embedding_id: the ChromaDB vector ID for this block (set after indexing).
    Enhanced with page range support, LLM-cleaned content, and chunking metadata.
    """
    __tablename__ = "blocks"

    id:                   Mapped[str]           = mapped_column(String,     primary_key=True, default=_new_uuid)
    doc_id:               Mapped[str]           = mapped_column(String,     ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    block_type:           Mapped[str]           = mapped_column(String(20), nullable=False, default="text")
    page:                 Mapped[int]           = mapped_column(Integer,    nullable=False, default=0)
    content:              Mapped[str]           = mapped_column(Text,       nullable=False)   # JSON string
    embedding_id:         Mapped[Optional[str]] = mapped_column(Text,       nullable=True)
    created_at:           Mapped[str]           = mapped_column(String,     nullable=False, default=_now_iso)
    
    # New columns
    page_range_start:     Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    page_range_end:       Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    llm_cleaned_content:  Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    extraction_metadata:  Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    chunk_index:          Mapped[int]           = mapped_column(Integer, nullable=False, default=0)
    overlap_with:         Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of block IDs

    document: Mapped["Document"] = relationship("Document", back_populates="blocks")

    def __repr__(self) -> str:
        return f"<Block id={self.id!r} type={self.block_type!r} page={self.page}>"


# ── Question ──────────────────────────────────────────────────────────────────

class Question(Base):
    """
    An exam question extracted from a past paper.
    prediction_score is computed by PredictionAgent and updated in place.
    Questions are NEVER fabricated — only extracted from ingested documents.
    Enhanced with source tracking, difficulty, and linked solutions.
    """
    __tablename__ = "questions"

    id:               Mapped[str]           = mapped_column(String,  primary_key=True, default=_new_uuid)
    doc_id:           Mapped[str]           = mapped_column(String,  ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    text:             Mapped[str]           = mapped_column(Text,    nullable=False)
    topic:            Mapped[Optional[str]] = mapped_column(Text,    nullable=True)
    year:             Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    prediction_score: Mapped[float]         = mapped_column(Float,   nullable=False, default=0.0)
    last_scored_at:   Mapped[Optional[str]] = mapped_column(String,  nullable=True)
    
    # New columns
    source_type:       Mapped[str]           = mapped_column(String(20), nullable=False, default="past_paper")
    difficulty:        Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    linked_solution_id:Mapped[Optional[str]] = mapped_column(String, ForeignKey("kb_blocks.id", ondelete="SET NULL"), nullable=True)
    frequency_score:   Mapped[float]         = mapped_column(Float, nullable=False, default=0.0)
    importance_score:  Mapped[float]         = mapped_column(Float, nullable=False, default=0.0)

    document: Mapped["Document"] = relationship("Document", back_populates="questions")
    linked_solution: Mapped[Optional["KBBlock"]] = relationship("KBBlock", foreign_keys=[linked_solution_id])

    def __repr__(self) -> str:
        return f"<Question id={self.id!r} topic={self.topic!r} score={self.prediction_score:.3f}>"


# ── KnowledgeBaseItem ─────────────────────────────────────────────────────────

class KnowledgeBaseItem(Base):
    """Textbooks, solution manuals, past papers, references."""
    __tablename__ = "knowledge_base_items"

    id:                Mapped[str]           = mapped_column(String, primary_key=True, default=_new_uuid)
    title:             Mapped[str]           = mapped_column(Text, nullable=False)
    item_type:         Mapped[str]           = mapped_column(String(30), nullable=False, default="textbook")
    course_id:         Mapped[Optional[str]] = mapped_column(String, ForeignKey("courses.id", ondelete="SET NULL"), nullable=True)
    file_path:         Mapped[str]           = mapped_column(Text, nullable=False)
    filename:          Mapped[str]           = mapped_column(Text, nullable=False)
    total_pages:       Mapped[int]           = mapped_column(Integer, nullable=False, default=0)
    processing_status: Mapped[str]           = mapped_column(String(20), nullable=False, default="pending")
    paired_with_id:    Mapped[Optional[str]] = mapped_column(String, ForeignKey("knowledge_base_items.id", ondelete="SET NULL"), nullable=True)
    metadata:          Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    uploaded_at:       Mapped[str]           = mapped_column(String, nullable=False, default=_now_iso)
    processed_at:      Mapped[Optional[str]] = mapped_column(String, nullable=True)

    course:      Mapped[Optional["Course"]]           = relationship("Course", back_populates="kb_items")
    paired_with: Mapped[Optional["KnowledgeBaseItem"]]= relationship("KnowledgeBaseItem", remote_side=[id], foreign_keys=[paired_with_id])
    blocks:      Mapped[list["KBBlock"]]              = relationship("KBBlock", back_populates="kb_item", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<KnowledgeBaseItem id={self.id!r} type={self.item_type!r} title={self.title!r}>"


# ── KBBlock ───────────────────────────────────────────────────────────────────

class KBBlock(Base):
    """Blocks extracted from knowledge base items."""
    __tablename__ = "kb_blocks"

    id:               Mapped[str]           = mapped_column(String, primary_key=True, default=_new_uuid)
    kb_item_id:       Mapped[str]           = mapped_column(String, ForeignKey("knowledge_base_items.id", ondelete="CASCADE"), nullable=False)
    block_type:       Mapped[str]           = mapped_column(String(20), nullable=False, default="text")
    page:             Mapped[int]           = mapped_column(Integer, nullable=False, default=0)
    content:          Mapped[str]           = mapped_column(Text, nullable=False)
    cleaned_content:  Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    question_number:  Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    topic:            Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    embedding_id:     Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata:         Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    created_at:       Mapped[str]           = mapped_column(String, nullable=False, default=_now_iso)

    kb_item: Mapped["KnowledgeBaseItem"] = relationship("KnowledgeBaseItem", back_populates="blocks")
    question_pairs: Mapped[list["QuestionSolutionPair"]] = relationship(
        "QuestionSolutionPair",
        foreign_keys="QuestionSolutionPair.question_block_id",
        back_populates="question_block"
    )
    solution_pairs: Mapped[list["QuestionSolutionPair"]] = relationship(
        "QuestionSolutionPair",
        foreign_keys="QuestionSolutionPair.solution_block_id",
        back_populates="solution_block"
    )

    def __repr__(self) -> str:
        return f"<KBBlock id={self.id!r} type={self.block_type!r} qnum={self.question_number!r}>"


# ── QuestionSolutionPair ──────────────────────────────────────────────────────

class QuestionSolutionPair(Base):
    """Links questions with their solutions from KB."""
    __tablename__ = "question_solution_pairs"

    id:                Mapped[str]           = mapped_column(String, primary_key=True, default=_new_uuid)
    question_block_id: Mapped[str]           = mapped_column(String, ForeignKey("kb_blocks.id", ondelete="CASCADE"), nullable=False)
    solution_block_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("kb_blocks.id", ondelete="CASCADE"), nullable=True)
    question_number:   Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    topic:             Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    difficulty:        Mapped[Optional[str]] = mapped_column(String(10), nullable=True)
    confidence_score:  Mapped[float]         = mapped_column(Float, nullable=False, default=0.5)
    created_at:        Mapped[str]           = mapped_column(String, nullable=False, default=_now_iso)

    question_block: Mapped["KBBlock"] = relationship("KBBlock", foreign_keys=[question_block_id], back_populates="question_pairs")
    solution_block: Mapped[Optional["KBBlock"]] = relationship("KBBlock", foreign_keys=[solution_block_id], back_populates="solution_pairs")

    def __repr__(self) -> str:
        return f"<QuestionSolutionPair qnum={self.question_number!r} conf={self.confidence_score:.2f}>"


# ── StudySession ──────────────────────────────────────────────────────────────

class StudySession(Base):
    """Track user study sessions for context awareness."""
    __tablename__ = "study_sessions"

    id:               Mapped[str]           = mapped_column(String, primary_key=True, default=_new_uuid)
    course_id:        Mapped[Optional[str]] = mapped_column(String, ForeignKey("courses.id", ondelete="CASCADE"), nullable=True)
    doc_id:           Mapped[Optional[str]] = mapped_column(String, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    started_at:       Mapped[str]           = mapped_column(String, nullable=False, default=_now_iso)
    ended_at:         Mapped[Optional[str]] = mapped_column(String, nullable=True)
    duration_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pages_viewed:     Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    topics_covered:   Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array
    metadata:         Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON

    course:       Mapped[Optional["Course"]]   = relationship("Course", back_populates="study_sessions")
    document:     Mapped[Optional["Document"]] = relationship("Document", back_populates="study_sessions")
    explanations: Mapped[list["Explanation"]]  = relationship("Explanation", back_populates="session", cascade="all, delete-orphan")
    conversations:Mapped[list["ConversationHistory"]] = relationship("ConversationHistory", back_populates="session", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<StudySession id={self.id!r} course_id={self.course_id!r}>"


# ── Explanation ───────────────────────────────────────────────────────────────

class Explanation(Base):
    """Store AI-generated explanations with full context."""
    __tablename__ = "explanations"

    id:             Mapped[str]           = mapped_column(String, primary_key=True, default=_new_uuid)
    session_id:     Mapped[Optional[str]] = mapped_column(String, ForeignKey("study_sessions.id", ondelete="CASCADE"), nullable=True)
    doc_id:         Mapped[Optional[str]] = mapped_column(String, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    page_number:    Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    query:          Mapped[str]           = mapped_column(Text, nullable=False)
    response:       Mapped[str]           = mapped_column(Text, nullable=False)
    context_blocks: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON array of block IDs
    selected_text:  Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_used:     Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    confidence:     Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    citations:      Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    created_at:     Mapped[str]           = mapped_column(String, nullable=False, default=_now_iso)

    session:  Mapped[Optional["StudySession"]] = relationship("StudySession", back_populates="explanations")
    document: Mapped[Optional["Document"]]     = relationship("Document", back_populates="explanations")

    def __repr__(self) -> str:
        return f"<Explanation id={self.id!r} session_id={self.session_id!r}>"


# ── ConversationHistory ───────────────────────────────────────────────────────

class ConversationHistory(Base):
    """Track chat messages for context continuity."""
    __tablename__ = "conversation_history"

    id:          Mapped[str]           = mapped_column(String, primary_key=True, default=_new_uuid)
    session_id:  Mapped[Optional[str]] = mapped_column(String, ForeignKey("study_sessions.id", ondelete="CASCADE"), nullable=True)
    role:        Mapped[str]           = mapped_column(String(10), nullable=False)
    content:     Mapped[str]           = mapped_column(Text, nullable=False)
    doc_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    timestamp:   Mapped[str]           = mapped_column(String, nullable=False, default=_now_iso)
    metadata:    Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON

    session: Mapped[Optional["StudySession"]] = relationship("StudySession", back_populates="conversations")

    def __repr__(self) -> str:
        return f"<ConversationHistory role={self.role!r} session_id={self.session_id!r}>"


# ── TopicAnalysis ─────────────────────────────────────────────────────────────

class TopicAnalysis(Base):
    """Track topic importance and frequency across materials."""
    __tablename__ = "topic_analysis"

    id:               Mapped[str]           = mapped_column(String, primary_key=True, default=_new_uuid)
    topic:            Mapped[str]           = mapped_column(Text, nullable=False, unique=True)
    course_id:        Mapped[Optional[str]] = mapped_column(String, ForeignKey("courses.id", ondelete="CASCADE"), nullable=True)
    frequency_count:  Mapped[int]           = mapped_column(Integer, nullable=False, default=0)
    question_count:   Mapped[int]           = mapped_column(Integer, nullable=False, default=0)
    kb_coverage:      Mapped[float]         = mapped_column(Float, nullable=False, default=0.0)
    importance_score: Mapped[float]         = mapped_column(Float, nullable=False, default=0.0)
    last_seen_year:   Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    metadata:         Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON
    updated_at:       Mapped[str]           = mapped_column(String, nullable=False, default=_now_iso)

    course: Mapped[Optional["Course"]] = relationship("Course", back_populates="topics")

    def __repr__(self) -> str:
        return f"<TopicAnalysis topic={self.topic!r} importance={self.importance_score:.2f}>"


# ── ProcessingJob ─────────────────────────────────────────────────────────────

class ProcessingJob(Base):
    """Track background processing tasks."""
    __tablename__ = "processing_jobs"

    id:            Mapped[str]           = mapped_column(String, primary_key=True, default=_new_uuid)
    job_type:      Mapped[str]           = mapped_column(String(30), nullable=False)
    target_id:     Mapped[str]           = mapped_column(String, nullable=False)
    status:        Mapped[str]           = mapped_column(String(20), nullable=False, default="pending")
    progress:      Mapped[float]         = mapped_column(Float, nullable=False, default=0.0)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at:    Mapped[Optional[str]] = mapped_column(String, nullable=True)
    completed_at:  Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at:    Mapped[str]           = mapped_column(String, nullable=False, default=_now_iso)
    metadata:      Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # JSON

    def __repr__(self) -> str:
        return f"<ProcessingJob id={self.id!r} type={self.job_type!r} status={self.status!r}>"