-- 002_file_system_and_knowledge_base.sql
-- Enhanced schema for file system, courses, knowledge base, and study tracking
-- SQLite-compatible schema

-- ============================================================================
-- COURSES
-- ============================================================================
CREATE TABLE IF NOT EXISTS courses (
    id          TEXT PRIMARY KEY,
    name        TEXT NOT NULL,
    code        TEXT,
    description TEXT,
    color       TEXT DEFAULT '#3b82f6',
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_courses_name ON courses(name);

-- ============================================================================
-- FILE SYSTEM NODES (Hierarchical structure)
-- ============================================================================
CREATE TABLE IF NOT EXISTS file_system_nodes (
    id          TEXT PRIMARY KEY,
    parent_id   TEXT REFERENCES file_system_nodes(id) ON DELETE CASCADE,
    course_id   TEXT REFERENCES courses(id) ON DELETE CASCADE,
    name        TEXT NOT NULL,
    node_type   TEXT NOT NULL DEFAULT 'file'
                    CHECK (node_type IN ('folder', 'file')),
    path        TEXT NOT NULL,  -- Full path for easy querying
    size_bytes  INTEGER DEFAULT 0,
    mime_type   TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_fs_parent ON file_system_nodes(parent_id);
CREATE INDEX IF NOT EXISTS idx_fs_course ON file_system_nodes(course_id);
CREATE INDEX IF NOT EXISTS idx_fs_path ON file_system_nodes(path);
CREATE INDEX IF NOT EXISTS idx_fs_type ON file_system_nodes(node_type);

-- ============================================================================
-- ENHANCED DOCUMENTS TABLE
-- ============================================================================
-- Add new columns to existing documents table
ALTER TABLE documents ADD COLUMN course_id TEXT REFERENCES courses(id) ON DELETE SET NULL;
ALTER TABLE documents ADD COLUMN file_system_node_id TEXT REFERENCES file_system_nodes(id) ON DELETE SET NULL;
ALTER TABLE documents ADD COLUMN processing_status TEXT DEFAULT 'pending'
    CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed'));
ALTER TABLE documents ADD COLUMN total_pages INTEGER DEFAULT 0;
ALTER TABLE documents ADD COLUMN file_size_bytes INTEGER DEFAULT 0;
ALTER TABLE documents ADD COLUMN file_path TEXT;
ALTER TABLE documents ADD COLUMN metadata TEXT;  -- JSON field for additional metadata

CREATE INDEX IF NOT EXISTS idx_documents_course ON documents(course_id);
CREATE INDEX IF NOT EXISTS idx_documents_fs_node ON documents(file_system_node_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(processing_status);

-- ============================================================================
-- DOCUMENT PAGES (Page-level metadata)
-- ============================================================================
CREATE TABLE IF NOT EXISTS document_pages (
    id          TEXT PRIMARY KEY,
    doc_id      TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    width       REAL,
    height      REAL,
    has_text    INTEGER DEFAULT 1,  -- Boolean: has extractable text
    has_images  INTEGER DEFAULT 0,  -- Boolean: contains images
    has_math    INTEGER DEFAULT 0,  -- Boolean: contains mathematical expressions
    thumbnail   TEXT,               -- Base64 encoded thumbnail
    processed   INTEGER DEFAULT 0,  -- Boolean: has been processed
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(doc_id, page_number)
);

CREATE INDEX IF NOT EXISTS idx_pages_doc ON document_pages(doc_id);
CREATE INDEX IF NOT EXISTS idx_pages_processed ON document_pages(processed);

-- ============================================================================
-- RAW EXTRACTIONS (Temporary storage for OCR output)
-- ============================================================================
CREATE TABLE IF NOT EXISTS raw_extractions (
    id          TEXT PRIMARY KEY,
    doc_id      TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    page_number INTEGER NOT NULL,
    raw_text    TEXT NOT NULL,
    extraction_metadata TEXT,  -- JSON: OCR confidence, method, etc.
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    processed   INTEGER DEFAULT 0,  -- Boolean: has been cleaned by LLM
    UNIQUE(doc_id, page_number)
);

CREATE INDEX IF NOT EXISTS idx_raw_doc ON raw_extractions(doc_id);
CREATE INDEX IF NOT EXISTS idx_raw_processed ON raw_extractions(processed);

-- ============================================================================
-- ENHANCED BLOCKS TABLE
-- ============================================================================
-- Add new columns to existing blocks table
ALTER TABLE blocks ADD COLUMN page_range_start INTEGER;
ALTER TABLE blocks ADD COLUMN page_range_end INTEGER;
ALTER TABLE blocks ADD COLUMN llm_cleaned_content TEXT;  -- LLM-enhanced version
ALTER TABLE blocks ADD COLUMN extraction_metadata TEXT;  -- JSON: confidence, method
ALTER TABLE blocks ADD COLUMN chunk_index INTEGER DEFAULT 0;  -- For ordered chunks
ALTER TABLE blocks ADD COLUMN overlap_with TEXT;  -- JSON: IDs of overlapping chunks

CREATE INDEX IF NOT EXISTS idx_blocks_page_range ON blocks(page_range_start, page_range_end);
CREATE INDEX IF NOT EXISTS idx_blocks_chunk ON blocks(doc_id, chunk_index);

-- ============================================================================
-- KNOWLEDGE BASE ITEMS
-- ============================================================================
CREATE TABLE IF NOT EXISTS knowledge_base_items (
    id              TEXT PRIMARY KEY,
    title           TEXT NOT NULL,
    item_type       TEXT NOT NULL DEFAULT 'textbook'
                        CHECK (item_type IN ('textbook', 'solution_manual', 'past_paper', 'reference', 'notes')),
    course_id       TEXT REFERENCES courses(id) ON DELETE SET NULL,
    file_path       TEXT NOT NULL,
    filename        TEXT NOT NULL,
    total_pages     INTEGER DEFAULT 0,
    processing_status TEXT DEFAULT 'pending'
                        CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
    paired_with_id  TEXT REFERENCES knowledge_base_items(id) ON DELETE SET NULL,  -- For textbook-manual pairs
    metadata        TEXT,  -- JSON: author, publisher, edition, etc.
    uploaded_at     TEXT NOT NULL DEFAULT (datetime('now')),
    processed_at    TEXT
);

CREATE INDEX IF NOT EXISTS idx_kb_type ON knowledge_base_items(item_type);
CREATE INDEX IF NOT EXISTS idx_kb_course ON knowledge_base_items(course_id);
CREATE INDEX IF NOT EXISTS idx_kb_status ON knowledge_base_items(processing_status);
CREATE INDEX IF NOT EXISTS idx_kb_paired ON knowledge_base_items(paired_with_id);

-- ============================================================================
-- KNOWLEDGE BASE BLOCKS (Similar to blocks but for KB items)
-- ============================================================================
CREATE TABLE IF NOT EXISTS kb_blocks (
    id          TEXT PRIMARY KEY,
    kb_item_id  TEXT NOT NULL REFERENCES knowledge_base_items(id) ON DELETE CASCADE,
    block_type  TEXT NOT NULL DEFAULT 'text'
                    CHECK (block_type IN ('text', 'equation', 'figure', 'table', 'question', 'solution')),
    page        INTEGER NOT NULL DEFAULT 0,
    content     TEXT NOT NULL,
    cleaned_content TEXT,
    question_number TEXT,  -- For indexed questions/solutions
    topic       TEXT,
    embedding_id TEXT,
    metadata    TEXT,  -- JSON: additional metadata
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_kb_blocks_item ON kb_blocks(kb_item_id);
CREATE INDEX IF NOT EXISTS idx_kb_blocks_type ON kb_blocks(block_type);
CREATE INDEX IF NOT EXISTS idx_kb_blocks_qnum ON kb_blocks(question_number);
CREATE INDEX IF NOT EXISTS idx_kb_blocks_topic ON kb_blocks(topic);

-- ============================================================================
-- QUESTION-SOLUTION PAIRS
-- ============================================================================
CREATE TABLE IF NOT EXISTS question_solution_pairs (
    id              TEXT PRIMARY KEY,
    question_block_id TEXT NOT NULL REFERENCES kb_blocks(id) ON DELETE CASCADE,
    solution_block_id TEXT REFERENCES kb_blocks(id) ON DELETE CASCADE,
    question_number TEXT,
    topic           TEXT,
    difficulty      TEXT CHECK (difficulty IN ('easy', 'medium', 'hard', 'unknown')),
    confidence_score REAL DEFAULT 0.5,  -- How confident we are about the pairing
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    UNIQUE(question_block_id, solution_block_id)
);

CREATE INDEX IF NOT EXISTS idx_qsp_question ON question_solution_pairs(question_block_id);
CREATE INDEX IF NOT EXISTS idx_qsp_solution ON question_solution_pairs(solution_block_id);
CREATE INDEX IF NOT EXISTS idx_qsp_topic ON question_solution_pairs(topic);
CREATE INDEX IF NOT EXISTS idx_qsp_qnum ON question_solution_pairs(question_number);

-- ============================================================================
-- ENHANCED QUESTIONS TABLE
-- ============================================================================
-- Add new columns to existing questions table
ALTER TABLE questions ADD COLUMN source_type TEXT DEFAULT 'past_paper'
    CHECK (source_type IN ('past_paper', 'textbook', 'practice', 'custom'));
ALTER TABLE questions ADD COLUMN difficulty TEXT 
    CHECK (difficulty IN ('easy', 'medium', 'hard', 'unknown'));
ALTER TABLE questions ADD COLUMN linked_solution_id TEXT REFERENCES kb_blocks(id) ON DELETE SET NULL;
ALTER TABLE questions ADD COLUMN frequency_score REAL DEFAULT 0.0;  -- How often this type appears
ALTER TABLE questions ADD COLUMN importance_score REAL DEFAULT 0.0;  -- Derived from KB analysis

CREATE INDEX IF NOT EXISTS idx_questions_source ON questions(source_type);
CREATE INDEX IF NOT EXISTS idx_questions_difficulty ON questions(difficulty);
CREATE INDEX IF NOT EXISTS idx_questions_linked ON questions(linked_solution_id);

-- ============================================================================
-- STUDY SESSIONS
-- ============================================================================
CREATE TABLE IF NOT EXISTS study_sessions (
    id          TEXT PRIMARY KEY,
    course_id   TEXT REFERENCES courses(id) ON DELETE CASCADE,
    doc_id      TEXT REFERENCES documents(id) ON DELETE SET NULL,
    started_at  TEXT NOT NULL DEFAULT (datetime('now')),
    ended_at    TEXT,
    duration_seconds INTEGER,
    pages_viewed TEXT,  -- JSON array of page numbers
    topics_covered TEXT,  -- JSON array of topics
    metadata    TEXT   -- JSON: notes, highlights, etc.
);

CREATE INDEX IF NOT EXISTS idx_sessions_course ON study_sessions(course_id);
CREATE INDEX IF NOT EXISTS idx_sessions_doc ON study_sessions(doc_id);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON study_sessions(started_at);

-- ============================================================================
-- EXPLANATIONS (Store AI-generated explanations with context)
-- ============================================================================
CREATE TABLE IF NOT EXISTS explanations (
    id              TEXT PRIMARY KEY,
    session_id      TEXT REFERENCES study_sessions(id) ON DELETE CASCADE,
    doc_id          TEXT REFERENCES documents(id) ON DELETE SET NULL,
    page_number     INTEGER,
    query           TEXT NOT NULL,
    response        TEXT NOT NULL,
    context_blocks  TEXT,  -- JSON array of block IDs used for context
    selected_text   TEXT,  -- User-highlighted text that prompted the question
    model_used      TEXT,
    confidence      TEXT CHECK (confidence IN ('high', 'medium', 'low', 'insufficient')),
    citations       TEXT,  -- JSON array of citation objects
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_explanations_session ON explanations(session_id);
CREATE INDEX IF NOT EXISTS idx_explanations_doc ON explanations(doc_id);
CREATE INDEX IF NOT EXISTS idx_explanations_page ON explanations(page_number);
CREATE INDEX IF NOT EXISTS idx_explanations_created ON explanations(created_at);

-- ============================================================================
-- TOPIC ANALYSIS (Track topic importance and frequency)
-- ============================================================================
CREATE TABLE IF NOT EXISTS topic_analysis (
    id              TEXT PRIMARY KEY,
    topic           TEXT NOT NULL UNIQUE,
    course_id       TEXT REFERENCES courses(id) ON DELETE CASCADE,
    frequency_count INTEGER DEFAULT 0,  -- How many times topic appears
    question_count  INTEGER DEFAULT 0,  -- Questions related to this topic
    kb_coverage     REAL DEFAULT 0.0,   -- Coverage in knowledge base (0-1)
    importance_score REAL DEFAULT 0.0,  -- Computed importance
    last_seen_year  INTEGER,
    metadata        TEXT,  -- JSON: subtopics, related topics, etc.
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_topic_course ON topic_analysis(course_id);
CREATE INDEX IF NOT EXISTS idx_topic_name ON topic_analysis(topic);
CREATE INDEX IF NOT EXISTS idx_topic_importance ON topic_analysis(importance_score);

-- ============================================================================
-- CONVERSATION HISTORY (Track chat messages for context)
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversation_history (
    id          TEXT PRIMARY KEY,
    session_id  TEXT REFERENCES study_sessions(id) ON DELETE CASCADE,
    role        TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content     TEXT NOT NULL,
    doc_context TEXT,  -- JSON: doc_id, page_number, selected_text
    timestamp   TEXT NOT NULL DEFAULT (datetime('now')),
    metadata    TEXT  -- JSON: tokens, model, etc.
);

CREATE INDEX IF NOT EXISTS idx_chat_session ON conversation_history(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_timestamp ON conversation_history(timestamp);

-- ============================================================================
-- PROCESSING JOBS (Track background processing tasks)
-- ============================================================================
CREATE TABLE IF NOT EXISTS processing_jobs (
    id          TEXT PRIMARY KEY,
    job_type    TEXT NOT NULL CHECK (job_type IN ('ingest', 'kb_index', 'question_pair', 'topic_extract', 'embed')),
    target_id   TEXT NOT NULL,  -- ID of document/KB item being processed
    status      TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    progress    REAL DEFAULT 0.0,  -- 0.0 to 1.0
    error_message TEXT,
    started_at  TEXT,
    completed_at TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
    metadata    TEXT  -- JSON: page_ranges, options, etc.
);

CREATE INDEX IF NOT EXISTS idx_jobs_type ON processing_jobs(job_type);
CREATE INDEX IF NOT EXISTS idx_jobs_target ON processing_jobs(target_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON processing_jobs(status);
