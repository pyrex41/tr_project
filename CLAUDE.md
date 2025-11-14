# Claude Code Instructions - Legal Analysis Backend

NEVER USE EMOJIS

## Project Overview

This is a **Legal Document Analysis System** that processes and analyzes Judge Boyle's expert witness rulings. The system combines traditional text search with AI-powered semantic analysis to provide deep insights into judicial patterns and expert testimony evaluation.

## Task Master AI Instructions
**Import Task Master's development workflow commands and guidelines:**
@./.taskmaster/CLAUDE.md

## Core System Architecture

### Technology Stack
- **Backend Framework:** FastAPI (async/await throughout)
- **Python Version:** 3.11+
- **Database:** SQLite with FTS5 (full-text search) + sqlite-vec (vector embeddings)
- **AI Models:**
  - GPT-5.1 (`reasoning_effort='max'`) for deep legal analysis
  - sentence-transformers (all-MiniLM-L6-v2) for embeddings
- **Frontend:** Elm (functional, type-safe) communicates via REST API

### Project Structure
```
backend/
├── api/
│   ├── models.py          # Pydantic request/response schemas
│   └── routes.py          # FastAPI endpoints
├── db/
│   └── database.py        # SQLite + FTS5 + sqlite-vec
├── services/
│   ├── parser.py          # Markdown AST parser
│   ├── metadata_extractor.py
│   ├── deep_analysis.py   # GPT-5.1 integration
│   ├── embeddings.py      # Vector generation
│   └── search.py          # Keyword + semantic search
├── scripts/
│   └── process_all_orders.py  # Parallel processing pipeline
├── utils/
│   ├── exceptions.py      # Custom exception hierarchy
│   └── logging_config.py  # Structured logging
├── main.py                # FastAPI application entry point
└── .env                   # Environment variables

frontend/
├── src/
│   ├── Main.elm           # Application entry point
│   ├── Pages/             # Dashboard, Search, OrderDetail, Orders
│   └── Components/        # Reusable UI components
├── public/
└── vite.config.js

data/
└── orders.db             # SQLite database (generated)

md_data/                  # 19 markdown court orders (source data)
```

## Development Guidelines

### Code Quality Standards
1. **Type Hints Required:** All functions must have complete type annotations
2. **Async/Await:** Use async patterns throughout for I/O operations
3. **Error Handling:** Custom exceptions at all layers with proper logging
4. **Logging:** Structured logging with request IDs and context
5. **Documentation:** Docstrings for all public functions and classes

### Performance Requirements
- **Processing Pipeline:** Complete all 19 orders in <45 minutes
- **API Response Times:**
  - Standard endpoints: <200ms
  - Semantic search: <500ms
- **Concurrent Processing:** Max 3 parallel GPT API calls (rate limiting)

### Cost Management
- **Estimated Cost:** $3-4 total for processing 19 orders with GPT-5.1
- **Token Tracking:** Log input/output tokens for all API calls
- **Retry Logic:** Exponential backoff with max 3 retries

## Task Dependencies & Workflow

### 12 Master Tasks (from tasks.json)
All tasks are tagged with "master" and must be completed sequentially respecting dependencies:

1. **Project Setup** (HIGH) - Dependencies: None
2. **Markdown AST Parser** (HIGH) - Dependencies: Task 1
3. **Basic Metadata Extraction** (MEDIUM) - Dependencies: Task 2
4. **Deep Legal Analysis with GPT-5.1** (HIGH) - Dependencies: Task 3
5. **Embedding Generation Service** (MEDIUM) - Dependencies: Task 4
6. **Database Schema and Storage** (HIGH) - Dependencies: Task 5
7. **Parallel Processing Pipeline** (HIGH) - Dependencies: Task 6
8. **FastAPI Backend and Core Endpoints** (MEDIUM) - Dependencies: Task 7
9. **Search Services** (MEDIUM) - Dependencies: Task 8
10. **Search API Endpoints** (HIGH) - Dependencies: Task 9
11. **Insights Generation** (HIGH) - Dependencies: Task 10
12. **Error Handling and Logging** (MEDIUM) - Dependencies: Task 11

**Reference:** See `.taskmaster/tasks/tasks.json` for detailed subtasks

## Technical Specifications

### 1. Markdown Parsing (Task 2)
- **Input:** 19 markdown files in `/md_data/` directory
- **Output:** OrderAST dataclass with structured sections
- **Extract:**
  - Case citations (regex: `([A-Z][\w\s]+v\.[\w\s]+,\s*\d+\s+F\.\s*[\w\d\s,]+\(\d{4}\))`)
  - Expert names (Dr., Ph.D., titles)
  - Legal entities and Daubert mentions
- **State Machine:** Track headers, blockquotes, paragraphs, citations

### 2. Deep Analysis (Task 4)
- **Model:** GPT-5.1 with `reasoning_effort='max'`
- **Output:** 2-3 page analysis with 10 sections:
  1. Case Context & Background
  2. Expert Witness Profile
  3. Challenged Methodology
  4. Daubert Standards Applied
  5. Court's Reasoning
  6. Exclusion/Admission Grounds
  7. Precedent Analysis
  8. Implications for Expert Testimony
  9. Judicial Patterns
  10. Key Takeaways
- **Retry Logic:** tenacity library with exponential backoff

### 3. Database Schema (Task 6)
```sql
-- Main orders table
orders (id, filename, raw_text, metadata_json, analysis_json)

-- FTS5 full-text search
orders_fts (filename, raw_text, analysis_text)

-- Vector embeddings
order_embeddings (order_id, embedding_blob)
analysis_chunks (id, order_id, section_name, content)
chunk_embeddings (chunk_id, embedding_blob)

-- Triggers to sync FTS5
```

### 4. API Endpoints (Tasks 8, 10)
```
GET  /health                    # Health check
GET  /api/stats                 # Database statistics
GET  /api/orders                # List all orders (with pagination)
GET  /api/orders/{id}           # Get single order with analysis
POST /api/search/keyword        # FTS5 search with ranking
POST /api/search/semantic       # RAG with vector similarity
GET  /api/insights              # Cross-order pattern analysis
```

### 5. CORS Configuration
```python
# Allow frontend on localhost:5173
origins = ["http://localhost:5173"]
```

## Environment Variables (.env)

```bash
OPENAI_API_KEY=sk-...          # Required for GPT-5.1
DATABASE_PATH=data/orders.db   # SQLite database location
LOG_LEVEL=INFO                 # Logging level
MAX_CONCURRENT_REQUESTS=3      # Rate limiting for GPT API
```

## Data Requirements

### Source Data
- **Location:** `/md_data/` directory
- **Format:** 19 markdown files containing Judge Boyle's rulings
- **Content:** Expert witness Daubert/702 orders
- **Processing:** Must preserve markdown structure during parsing

### Generated Data
- **Database:** `data/orders.db` (created by pipeline)
- **Embeddings:** 384-dimensional vectors (all-MiniLM-L6-v2)
- **Analysis:** JSON stored in database with structured sections

## AI Integration Guidelines

### GPT-5.1 Usage
1. **Always use AsyncOpenAI** for non-blocking I/O
2. **Set `reasoning_effort='max'`** for deepest analysis
3. **Track tokens and costs** in logs
4. **Implement retry logic** for transient failures
5. **Parse JSON responses** with error handling

### Embedding Generation
1. **Model:** `sentence-transformers/all-MiniLM-L6-v2`
2. **Dimensions:** 384
3. **Normalize:** L2 normalization for cosine similarity
4. **Batch Processing:** Embed full order + individual analysis sections
5. **Storage:** Binary blobs in SQLite (sqlite-vec format)

## Error Handling Requirements

### Custom Exception Hierarchy
```python
class LegalAnalysisException(Exception): pass
class ParsingError(LegalAnalysisException): pass
class DatabaseError(LegalAnalysisException): pass
class AIServiceError(LegalAnalysisException): pass
class SearchError(LegalAnalysisException): pass
```

### Logging Standards
- **Format:** JSON structured logs with timestamps
- **Context:** Request ID, user context, operation name
- **Levels:** DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Sensitive Data:** Never log API keys or full prompts

## Testing & Validation

### Manual Testing Checklist
1. Process all 19 orders successfully
2. Verify FTS5 search returns relevant results
3. Test semantic search with sample queries
4. Validate API response times meet requirements
5. Check database integrity and triggers
6. Verify CORS allows frontend connections

### Performance Benchmarks
- Pipeline completion: <45 minutes for 19 orders
- API latency: <200ms average
- Semantic search: <500ms with vector similarity
- Database queries: <50ms for keyword search

## Dependencies (requirements.txt)

```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
openai>=1.3.0
sentence-transformers>=2.2.2
sqlite-vec>=0.1.0
tenacity>=8.2.3
python-dotenv>=1.0.0
pydantic>=2.5.0
pydantic-settings>=2.1.0
aiosqlite>=0.19.0
numpy>=1.24.0
```

## Development Workflow

### Phase 1: Foundation (Tasks 1-3)
1. Set up virtual environment and dependencies
2. Create directory structure
3. Implement markdown parser with regex patterns
4. Extract basic metadata (no AI)

### Phase 2: AI Integration (Tasks 4-5)
1. Configure OpenAI AsyncClient
2. Implement deep analysis with GPT-5.1
3. Add embedding generation service
4. Test with 1-2 sample orders

### Phase 3: Data Layer (Tasks 6-7)
1. Design database schema with FTS5 + sqlite-vec
2. Implement DatabaseService with insert methods
3. Create parallel processing pipeline
4. Process all 19 orders

### Phase 4: API Layer (Tasks 8-10)
1. Build FastAPI application with CORS
2. Implement core endpoints (health, stats, orders)
3. Add search services (keyword + semantic)
4. Create search API endpoints

### Phase 5: Polish (Tasks 11-12)
1. Implement insights generation endpoint
2. Add comprehensive error handling
3. Configure structured logging
4. Test end-to-end with frontend

## Critical Rules

### Data Integrity
- **NEVER modify source markdown files** in `/md_data/`
- **ALWAYS validate** parsed AST structure before processing
- **BACKUP database** before schema changes
- **LOG all processing errors** with context

### Security
- **API keys in .env only** - never commit to git
- **Validate all user input** with Pydantic models
- **Sanitize database queries** (use parameterized queries)
- **Rate limit API endpoints** to prevent abuse

### Cost Control
- **Semaphore limiting** to max 3 concurrent GPT calls
- **Cache embeddings** to avoid regeneration
- **Monitor token usage** for budget tracking
- **Fail fast** on API errors to avoid wasted calls

## Success Criteria

The project is complete when:
1. ✅ All 19 orders processed and stored in database
2. ✅ FTS5 keyword search returns relevant results
3. ✅ Semantic search uses vector embeddings effectively
4. ✅ API endpoints respond within latency requirements
5. ✅ Frontend can query and display order analyses
6. ✅ Insights endpoint provides cross-order patterns
7. ✅ Error handling covers all failure scenarios
8. ✅ Logging provides clear debugging information

## Notes

- **Total Development Time:** ~8.5 hours estimated
- **Processing Time:** <45 minutes for initial data load
- **Total Cost:** $3-4 in OpenAI API calls
- **Database Size:** ~50-100MB with embeddings
- **Frontend:** Elm frontend in separate directory

---

**Task Progress:** Track via Task Master at `.taskmaster/tasks/tasks.json`
**Documentation:** This file serves as the source of truth for development
