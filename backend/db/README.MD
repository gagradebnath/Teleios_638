# Database Layer — `backend/db/`

This document covers every file in the database layer, explains every design decision, and gives copy-paste examples for anyone reading, using, or modifying this code.

---

## Table of Contents

1. [Overview](#overview)
2. [Folder Structure](#folder-structure)
3. [Dependencies](#dependencies)
4. [Schema](#schema)
   - [documents](#documents-table)
   - [blocks](#blocks-table)
   - [questions](#questions-table)
   - [Indexes](#indexes)
5. [File-by-file Reference](#file-by-file-reference)
   - [db/session.py](#dbsessionpy)
   - [db/models/models.py](#dbmodelsmodelspy)
   - [db/models/\_\_init\_\_.py](#dbmodels__init__py)
   - [db/\_\_init\_\_.py](#db__init__py)
   - [db/migrations/001\_initial.sql](#dbmigrations001_initialsql)
   - [services/sql\_store.py](#servicessql_storepy)
6. [Lifecycle — startup and shutdown](#lifecycle--startup-and-shutdown)
7. [Working with sessions](#working-with-sessions)
8. [SQLStoreService — full API reference](#sqlstoreservice--full-api-reference)
9. [Adding a new table](#adding-a-new-table)
10. [Adding a new column to an existing table](#adding-a-new-column-to-an-existing-table)
11. [Running the tests](#running-the-tests)
12. [Common mistakes and how to avoid them](#common-mistakes-and-how-to-avoid-them)
13. [Design decisions and why](#design-decisions-and-why)

---

## Overview

The database layer is a **SQLite-backed async store** built on:

- **SQLAlchemy 2.x** for ORM models, metadata, and the async engine
- **aiosqlite** as the async SQLite driver
- **structlog** for structured JSON logging

Everything is async-first. All database access must happen inside an `async` function. There is no synchronous database interface anywhere in this layer.

The layer is split into two concerns:

- `db/` — engine, session factory, ORM models, and schema migrations. This is the low-level plumbing.
- `services/sql_store.py` — the high-level service that the rest of the application calls. It wraps all SQL behind clean Python methods so callers never write raw SQL themselves.

---

## Folder Structure

```
backend/
├── db/
│   ├── __init__.py              # re-exports init_db, get_async_session, models
│   ├── session.py               # engine + session factory + Base
│   ├── models/
│   │   ├── __init__.py          # re-exports Document, Block, Question
│   │   └── models.py            # SQLAlchemy ORM table definitions
│   └── migrations/
│       └── 001_initial.sql      # reference SQL (tables are auto-created by SQLAlchemy)
│
└── services/
    └── sql_store.py             # SQLStoreService — the only class the app calls
```

---

## Dependencies

Install these into your virtualenv before using anything in this layer:

```
sqlalchemy>=2.0
aiosqlite
structlog
```

All three are standard pip packages. There is no Alembic, no database server, no Docker required. SQLite is built into Python.

---

## Schema

There are three tables. Their relationships are:

```
documents  ──< blocks     (one document has many blocks)
documents  ──< questions  (one document has many questions)
```

Deleting a document cascades and deletes all its blocks and questions automatically.

### `documents` table

Represents a single ingested PDF file — either a textbook or a past exam paper.

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| `id` | TEXT | NO | uuid4 | Primary key. Always a UUID string, e.g. `"a1b2c3d4-..."` |
| `title` | TEXT | NO | — | Human-readable title of the document |
| `doc_type` | TEXT(20) | NO | `"unknown"` | Must be one of: `"textbook"`, `"past_paper"`, `"unknown"` |
| `year` | INTEGER | YES | NULL | Publication or exam year, e.g. `2023` |
| `subject` | TEXT | YES | NULL | Subject area, e.g. `"mathematics"` |
| `filename` | TEXT | NO | — | Original filename of the uploaded PDF |
| `uploaded_at` | TEXT | NO | now (UTC ISO) | ISO 8601 timestamp string, e.g. `"2024-01-15T10:30:00+00:00"` |

**Important:** `doc_type` is enforced at the SQL level with a CHECK constraint. Inserting any value other than `"textbook"`, `"past_paper"`, or `"unknown"` will raise an `IntegrityError`. Do not add new types without updating both the model and the migration file.

### `blocks` table

A single parsed chunk extracted from a document page. Every document is broken into blocks during ingestion. A block could be a paragraph of text, a LaTeX equation, a figure, or a table.

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| `id` | TEXT | NO | uuid4 | Primary key |
| `doc_id` | TEXT | NO | — | Foreign key → `documents.id`. Cascades on delete. |
| `block_type` | TEXT(20) | NO | `"text"` | Must be one of: `"text"`, `"equation"`, `"figure"`, `"table"` |
| `page` | INTEGER | NO | `0` | Zero-indexed page number within the source document |
| `content` | TEXT | NO | — | JSON string. Schema varies by `block_type` (see below) |
| `embedding_id` | TEXT | YES | NULL | ChromaDB vector ID. Set after the block is indexed. NULL means not yet embedded. |
| `created_at` | TEXT | NO | now (UTC ISO) | ISO 8601 timestamp string |

**Content JSON schema by block_type:**

```python
# block_type = "text"
{"text": "The mitochondria is the powerhouse of the cell."}

# block_type = "equation"
{"latex": "E = mc^2", "label": "energy-mass equivalence"}

# block_type = "figure"
{"caption": "Figure 3: Cell membrane", "image_ref": "fig_003.png"}

# block_type = "table"
{"headers": ["Year", "Score"], "rows": [["2020", "72"], ["2021", "85"]]}
```

`content` is stored as a plain JSON string. The service layer serializes dicts to strings before inserting, and it is the caller's responsibility to `json.loads()` the content after fetching it.

### `questions` table

An exam question extracted from a past paper. Questions are **never fabricated** — they are only inserted when extracted from an ingested document. `prediction_score` is computed by a separate prediction agent and updated in place.

| Column | Type | Nullable | Default | Notes |
|---|---|---|---|---|
| `id` | TEXT | NO | uuid4 | Primary key |
| `doc_id` | TEXT | NO | — | Foreign key → `documents.id`. Cascades on delete. |
| `text` | TEXT | NO | — | Full question text |
| `topic` | TEXT | YES | NULL | Topic tag, e.g. `"calculus"`, `"thermodynamics"` |
| `year` | INTEGER | YES | NULL | Year the question appeared on an exam |
| `prediction_score` | REAL | NO | `0.0` | Float between 0.0 and 1.0. Higher = more likely to appear again. |
| `last_scored_at` | TEXT | YES | NULL | ISO 8601 timestamp of when `prediction_score` was last updated. NULL means never scored. |

### Indexes

These indexes are defined in the migration SQL and are automatically present:

| Index | Table | Column | Purpose |
|---|---|---|---|
| `idx_blocks_doc_id` | blocks | doc_id | Fast lookup of all blocks for a document |
| `idx_blocks_type` | blocks | block_type | Filter blocks by type |
| `idx_questions_doc_id` | questions | doc_id | Fast lookup of all questions for a document |
| `idx_questions_topic` | questions | topic | Filter/group questions by topic |
| `idx_questions_year` | questions | year | Filter questions by exam year |

---

## File-by-file Reference

### `db/session.py`

This is the foundation of the entire database layer. It owns three things:

**1. `Base` — the declarative base class**

```python
class Base(DeclarativeBase):
    pass
```

Every ORM model must inherit from this `Base`. SQLAlchemy uses `Base.metadata` to track all registered tables and to run `CREATE TABLE` statements. If a model does not inherit from this `Base`, its table will never be created.

**2. Module-level singletons**

```python
_engine:          AsyncEngine | None        = None
_session_factory: async_sessionmaker | None = None
```

These are `None` at import time. They are only set when `init_db()` is called. If you try to use `get_async_session()` before calling `init_db()`, you will get a clear `RuntimeError`. Do not import and use these directly — always go through the public functions.

**3. `init_db(db_url)` — must be called once at startup**

```python
await init_db("sqlite+aiosqlite:///./data/teleios.db")
```

This function:
- Normalises `sqlite://` to `sqlite+aiosqlite://` automatically, so you can pass either form
- Creates the directory for the `.db` file if it does not already exist
- Creates the async engine and session factory and stores them in the module-level singletons
- Imports the ORM models to register them with `Base.metadata`
- Runs `CREATE TABLE IF NOT EXISTS` for all registered models

You must call this exactly once before any database access. The right place is your application's lifespan startup handler (e.g. FastAPI's `@asynccontextmanager` lifespan).

**4. `get_async_session()` — context manager for all DB access**

```python
async with get_async_session() as session:
    result = await session.execute(text("SELECT 1"))
```

Yields an `AsyncSession`. On any exception, it automatically rolls back the transaction before re-raising. You are responsible for calling `await session.commit()` when you want to persist writes. The session is closed automatically when the `async with` block exits.

**5. `close_db()` — must be called once at shutdown**

```python
await close_db()
```

Disposes the engine (closes all pooled connections) and resets both singletons to `None`. Call this in your application's lifespan shutdown handler. After this is called, any call to `get_async_session()` will raise `RuntimeError` rather than crashing with a confusing disposed-engine error.

---

### `db/models/models.py`

Defines the three ORM models. Each model maps directly to one database table.

**Timestamp storage:** All timestamps are stored as `String` columns containing ISO 8601 strings (e.g. `"2024-01-15T10:30:00+00:00"`). SQLite has no native `DATETIME` type — it stores everything as text anyway. Using `String` makes this explicit and avoids SQLAlchemy type-coercion surprises with the `aiosqlite` driver.

**Primary keys:** All primary keys are `String` columns holding UUID4 strings. They are generated in Python (not by the database) using `uuid.uuid4()`. This means IDs are always available immediately after object creation, before any database round-trip.

**Relationships:** The `relationship()` calls on `Document` are for ORM navigation only (e.g. `doc.blocks`, `doc.questions`). They are not needed for raw SQL queries through `SQLStoreService`. `cascade="all, delete-orphan"` means that when you delete a `Document` ORM object, SQLAlchemy will also delete all its `Block` and `Question` children automatically.

**Adding a new model:** Create your class in `models.py` inheriting from `Base`. Import it inside `init_db()` in `session.py` so it gets registered with `Base.metadata` before `create_all` runs. See [Adding a new table](#adding-a-new-table) for the full steps.

---

### `db/models/__init__.py`

```python
from db.models.models import Document, Block, Question
__all__ = ["Document", "Block", "Question"]
```

A simple re-export so other modules can write `from db.models import Document` instead of `from db.models.models import Document`.

---

### `db/__init__.py`

```python
from db.session import init_db, get_async_session
from db.models import Document, Block, Question
__all__ = ["init_db", "get_async_session", "Document", "Block", "Question"]
```

The top-level convenience re-export. Application code can do `from db import init_db, Document` instead of navigating the subpackage.

---

### `db/migrations/001_initial.sql`

This file is **reference documentation only**. Tables are not created by running this SQL file — they are created automatically by `init_db()` via `Base.metadata.create_all`. 

The SQL file exists so that:
- You can read the schema without running Python
- You have a record of the intended CHECK constraints and indexes
- Future migration tooling (e.g. Alembic) has a starting point

If you add a table or column to the ORM models, also update this file to keep it in sync with reality. Do not rely on it as a source of truth — the ORM models are the source of truth.

---

### `services/sql_store.py`

The only class the rest of the application should ever call for database writes. It is a stateless service — instantiate it anywhere with `SQLStoreService()`, no constructor arguments needed.

All methods use raw SQL via `sqlalchemy.text()` rather than ORM constructs. This is deliberate — raw SQL is explicit, easy to read, and straightforward to debug. The ORM models exist for schema definition and `create_all`, not for query building.

See [SQLStoreService — full API reference](#sqlstoreservice--full-api-reference) below.

---

## Lifecycle — startup and shutdown

In a FastAPI application, wire the database into the lifespan like this:

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from db.session import init_db, close_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db("sqlite+aiosqlite:///./data/teleios.db")
    yield
    # Shutdown
    await close_db()

app = FastAPI(lifespan=lifespan)
```

The database URL can come from an environment variable:

```python
import os
DB_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/teleios.db")
await init_db(DB_URL)
```

**In tests**, call `init_db` and `close_db` manually around your test suite (see `backend/test.py` for the pattern using `asyncio.run()`).

---

## Working with sessions

Always use the `get_async_session()` context manager. Never instantiate `AsyncSession` directly.

**Reading data:**

```python
from sqlalchemy import text
from db.session import get_async_session

async def get_document(doc_id: str):
    async with get_async_session() as session:
        result = await session.execute(
            text("SELECT id, title, doc_type FROM documents WHERE id = :id"),
            {"id": doc_id}
        )
        row = result.fetchone()
        return dict(row._mapping) if row else None
```

**Writing data:**

```python
async def mark_document_processed(doc_id: str):
    async with get_async_session() as session:
        await session.execute(
            text("UPDATE documents SET doc_type = :t WHERE id = :id"),
            {"t": "textbook", "id": doc_id}
        )
        await session.commit()  # ← never forget this for writes
```

**Important rules:**
- Always call `await session.commit()` after any INSERT, UPDATE, or DELETE. The session will not auto-commit.
- Never use `?` as a placeholder — SQLAlchemy's `text()` uses named placeholders (`:name`). The `?` style is only for the `execute_query` helper in `SQLStoreService`, which converts them internally.
- Each `async with get_async_session()` block is its own transaction. Keep transactions short — don't hold a session open across unrelated operations.

---

## SQLStoreService — full API reference

Import and instantiate:

```python
from services.sql_store import SQLStoreService
store = SQLStoreService()
```

---

### `insert_document(data: dict) -> str`

Inserts a row into the `documents` table. Returns the new document's UUID string.

**Required keys in `data`:**

| Key | Type | Notes |
|---|---|---|
| `title` | str | Human-readable document title |
| `filename` | str | Original PDF filename |

**Optional keys in `data`:**

| Key | Type | Default | Notes |
|---|---|---|---|
| `doc_type` | str | `"unknown"` | Must be `"textbook"`, `"past_paper"`, or `"unknown"` |
| `year` | int | `None` | Publication or exam year |
| `subject` | str | `None` | Subject area |

**Example:**

```python
doc_id = await store.insert_document({
    "title": "A-Level Mathematics 2023",
    "doc_type": "past_paper",
    "year": 2023,
    "subject": "mathematics",
    "filename": "amath_2023.pdf",
})
print(doc_id)  # "a1b2c3d4-e5f6-..."
```

---

### `insert_block(data: dict) -> str`

Inserts a row into the `blocks` table. Returns the new block's UUID string.

**Required keys in `data`:**

| Key | Type | Notes |
|---|---|---|
| `doc_id` | str | UUID of the parent document. Must already exist. |
| `content` | dict or str | Block content. If a dict is passed, it is serialized to JSON automatically. |

**Optional keys in `data`:**

| Key | Type | Default | Notes |
|---|---|---|---|
| `block_type` | str | `"text"` | Must be `"text"`, `"equation"`, `"figure"`, or `"table"` |
| `page` | int | `0` | Zero-indexed page number |

**Example:**

```python
block_id = await store.insert_block({
    "doc_id": doc_id,
    "block_type": "equation",
    "page": 4,
    "content": {"latex": "\\int_0^\\infty e^{-x^2} dx = \\frac{\\sqrt{\\pi}}{2}"},
})
```

---

### `insert_question(data: dict) -> str`

Inserts a row into the `questions` table. Returns the new question's UUID string.

**Required keys in `data`:**

| Key | Type | Notes |
|---|---|---|
| `doc_id` | str | UUID of the parent document. Must already exist. |
| `text` | str | Full text of the question |

**Optional keys in `data`:**

| Key | Type | Default | Notes |
|---|---|---|---|
| `topic` | str | `None` | Topic tag |
| `year` | int | `None` | Exam year |
| `prediction_score` | float | `0.0` | Initial score. Usually left at default and updated later by the prediction agent. |

**Example:**

```python
question_id = await store.insert_question({
    "doc_id": doc_id,
    "text": "Prove by induction that the sum of the first n natural numbers is n(n+1)/2.",
    "topic": "proof",
    "year": 2023,
})
```

---

### `update_prediction_score(question_id: str, score: float) -> None`

Updates the `prediction_score` and `last_scored_at` timestamp for a single question. Called by the prediction agent after it has computed a new score.

**Example:**

```python
await store.update_prediction_score(question_id, 0.87)
```

---

### `execute_query(sql: str, params: list = None) -> list[dict]`

Runs an arbitrary raw SQL SELECT and returns the results as a list of dicts, where each dict maps column name → value.

This is a **read-only escape hatch** for queries that don't fit the other methods. Do not use it for writes — use a direct session instead.

Uses `?` positional placeholders (SQLite style). Internally, these are converted to named SQLAlchemy parameters before execution.

**Example:**

```python
rows = await store.execute_query(
    "SELECT id, text, prediction_score FROM questions WHERE topic = ? ORDER BY prediction_score DESC LIMIT 10",
    ["calculus"]
)
for row in rows:
    print(row["text"], row["prediction_score"])
```

**Returns:** An empty list `[]` if no rows match. Never returns `None`.

---

## Adding a new table

Follow these steps exactly, in this order. Skipping any step will break things.

**Step 1 — Add the model to `db/models/models.py`:**

```python
class Tag(Base):
    __tablename__ = "tags"

    id:      Mapped[str] = mapped_column(String, primary_key=True, default=_new_uuid)
    name:    Mapped[str] = mapped_column(Text, nullable=False, unique=True)
    color:   Mapped[Optional[str]] = mapped_column(Text, nullable=True)
```

**Step 2 — Re-export it from `db/models/__init__.py`:**

```python
from db.models.models import Document, Block, Question, Tag
__all__ = ["Document", "Block", "Question", "Tag"]
```

**Step 3 — Import it in `init_db()` inside `db/session.py`:**

```python
from db.models.models import Document, Block, Question, Tag  # noqa: F401
```

This import must happen before `Base.metadata.create_all` runs. That line inside `init_db()` scans `Base.metadata` for all registered models — if your model hasn't been imported yet, its table won't be created.

**Step 4 — Re-export from `db/__init__.py` if needed:**

```python
from db.models import Document, Block, Question, Tag
```

**Step 5 — Update `db/migrations/001_initial.sql`** to include the new `CREATE TABLE` statement for reference.

**Step 6 — Add service methods to `SQLStoreService`** for inserting and querying the new table.

The table will be auto-created next time `init_db()` runs. For a database that already exists on disk, `CREATE TABLE IF NOT EXISTS` means it will be created without touching the existing tables.

---

## Adding a new column to an existing table

SQLAlchemy's `create_all` does **not** add columns to already-existing tables. It only creates tables that don't exist yet.

For a development database you don't mind resetting, just delete the `.db` file and let `init_db()` recreate it from scratch.

For a database with data you want to keep, run an `ALTER TABLE` manually:

```python
from sqlalchemy import text
from db.session import get_async_session

async def migrate():
    async with get_async_session() as session:
        await session.execute(text(
            "ALTER TABLE questions ADD COLUMN difficulty TEXT"
        ))
        await session.commit()
```

Then add the column to the ORM model in `models.py`:

```python
difficulty: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
```

And update `001_initial.sql` to include the column so the reference stays accurate.

---

## Running the tests

The test file is at `backend/test.py`. Run it from the project root:

```
python -u backend/test.py
```

or via pytest directly:

```
pytest backend/test.py -v
```

The tests use a temporary SQLite database created in a system temp directory. It is discarded after the test run. You do not need a real database file on disk.

**Test coverage:**

| Test | What it checks |
|---|---|
| `test_tables_exist` | All three tables are created by `init_db()` |
| `test_insert_document_and_fetch` | `insert_document` writes a row and `execute_query` reads it back correctly |
| `test_block_and_question_roundtrip` | Full round-trip: insert document → insert block → insert question → update score → verify via `execute_query` |

---

## Common mistakes and how to avoid them

**Forgetting `await session.commit()` after a write**

The session does not auto-commit. If you INSERT or UPDATE and don't commit, the data exists only inside the current transaction and is lost when the session closes. Always end a write block with `await session.commit()`.

**Using `?` placeholders with `session.execute(text(...))`**

`sqlalchemy.text()` uses named placeholders (`:name`), not positional `?`. Using `?` directly will raise an error. The only place `?` works is through `SQLStoreService.execute_query()`, which converts them automatically.

**Calling `get_async_session()` before `init_db()`**

You will get: `RuntimeError: Database not initialised`. Make sure `await init_db(url)` is called during application startup before any request handler or service method runs.

**Adding a model but forgetting to import it in `init_db()`**

The import inside `init_db()` is what registers the model with `Base.metadata`. Without it, `create_all` has no knowledge of the table and will never create it. The model file existing is not enough — it must be imported.

**Passing an invalid `doc_type`**

The valid values are exactly: `"textbook"`, `"past_paper"`, `"unknown"`. Anything else raises an `IntegrityError` from SQLite's CHECK constraint. This is enforced at the database level, not in Python.

**Storing a Python dict in `content` without serializing**

`content` is a `TEXT` column. If you pass a Python dict to a raw `session.execute()` INSERT, SQLite will reject it. Always `json.dumps()` the dict first. `SQLStoreService.insert_block()` does this automatically — but if you write raw SQL elsewhere, you must do it yourself.

---

## Design decisions and why

**Why SQLite and not PostgreSQL?**

SQLite requires zero infrastructure — no server, no Docker, no connection string management beyond a file path. For a student-facing tool that runs on a single machine, it is the right default. Migrating to PostgreSQL later would mean changing the connection URL and driver (`asyncpg` instead of `aiosqlite`) — the SQLAlchemy layer above that would be largely unchanged.

**Why async?**

The application is a FastAPI service that handles concurrent requests. Using an async database driver means the event loop is never blocked while waiting on I/O. A blocking synchronous call inside an async handler would stall all other requests sharing that event loop.

**Why raw SQL in `SQLStoreService` instead of ORM queries?**

ORM query builders (like `session.query(Document).filter(...)`) add a layer of abstraction that makes simple queries harder to read and debug. Raw `text()` SQL is explicit — you can paste it directly into a SQLite browser to test it. The ORM models are still used for schema definition and `create_all`, which is where they add the most value.

**Why store timestamps as TEXT strings?**

SQLite has no native `DATETIME` type. It stores dates as text, integers, or reals depending on what you give it. SQLAlchemy's `DateTime` type with the `aiosqlite` driver can produce inconsistent results depending on the driver version. Storing ISO 8601 strings explicitly (e.g. `"2024-01-15T10:30:00+00:00"`) is unambiguous, portable, and human-readable. The trade-off is that you cannot use SQLite's `datetime()` functions reliably on these values — but none of the current queries need that.

**Why are all primary keys UUIDs and not auto-increment integers?**

UUID primary keys mean IDs are generated in Python before the INSERT, so the caller knows the ID immediately without a round-trip. This makes it easy to create related records in a single operation. It also future-proofs the schema — if the application ever needs to distribute or merge data across databases, integer primary keys would collide; UUIDs won't.