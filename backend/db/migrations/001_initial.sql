CREATE TABLE IF NOT EXISTS documents (
    id          TEXT PRIMARY KEY,
    title       TEXT NOT NULL,
    doc_type    TEXT NOT NULL CHECK (doc_type IN ('textbook','past_paper','unknown')),
    year        INTEGER,
    subject     TEXT,
    filename    TEXT NOT NULL,
    uploaded_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS blocks (
    id           TEXT PRIMARY KEY,
    doc_id       TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    block_type   TEXT NOT NULL CHECK (block_type IN ('text','equation','figure','table')),
    page         INTEGER NOT NULL DEFAULT 0,
    content      TEXT NOT NULL,
    embedding_id TEXT,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS questions (
    id               TEXT PRIMARY KEY,
    doc_id           TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    text             TEXT NOT NULL,
    topic            TEXT,
    year             INTEGER,
    prediction_score REAL NOT NULL DEFAULT 0.0,
    last_scored_at   TEXT
);

CREATE INDEX IF NOT EXISTS idx_blocks_doc_id    ON blocks(doc_id);
CREATE INDEX IF NOT EXISTS idx_blocks_type      ON blocks(block_type);
CREATE INDEX IF NOT EXISTS idx_questions_doc_id ON questions(doc_id);
CREATE INDEX IF NOT EXISTS idx_questions_topic  ON questions(topic);
CREATE INDEX IF NOT EXISTS idx_questions_year   ON questions(year);