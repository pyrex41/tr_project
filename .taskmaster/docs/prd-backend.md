# PRD: Backend & Data Processing Pipeline
## Know Your Judge - Expert Witness Analysis

**Version:** 1.0  
**Date:** November 14, 2025  
**Owner:** Engineering Team  
**Timeline:** 3 hours (POC phase)

---

## 1. Overview

### 1.1 Purpose
Build a FastAPI backend that processes 19 expert witness orders from Judge Jane J. Boyle, generates deep legal analysis using GPT-5.1, stores structured data in SQLite with vector embeddings, and exposes REST APIs for search and retrieval.

### 1.2 Success Criteria
- ✅ Process all 19 orders in under 45 minutes (with parallel GPT-5.1 calls)
- ✅ Generate comprehensive legal analysis (2-3 pages per order)
- ✅ Enable sub-100ms FTS5 keyword search
- ✅ Enable semantic/RAG search with <500ms latency
- ✅ RESTful API with <200ms average response time
- ✅ Production-ready error handling and logging

### 1.3 Technology Stack
- **Runtime:** Python 3.11+
- **Web Framework:** FastAPI 0.104+
- **Database:** SQLite 3.42+ with FTS5 and sqlite-vec extensions
- **LLM:** OpenAI GPT-5.1 (with max reasoning effort)
- **Embeddings:** sentence-transformers (all-MiniLM-L6-v2)
- **Async:** asyncio with rate limiting (Semaphore)

---

## 2. Data Processing Pipeline

### 2.1 Input Data
- **Format:** 19 Markdown files in `/mnt/user-data/uploads/md_data/` directory
- **Structure:** Judicial orders with case names, dates, expert testimony, rulings
- **Size:** ~5-15KB per file (text)

### 2.2 Processing Stages

#### Stage 1: Markdown AST Parser
**File:** `services/parser.py`

Parse markdown into structured Abstract Syntax Tree:

```python
@dataclass
class OrderSection:
    type: str  # 'header', 'paragraph', 'quote', 'citation'
    content: str
    level: int  # for headers
    line_start: int
    line_end: int
    metadata: Dict[str, Any]

@dataclass
class OrderAST:
    case_name: str
    date: Optional[str]
    docket_number: Optional[str]
    sections: List[OrderSection]
    citations: List[str]  # extracted case citations
    entities: Dict[str, List[str]]  # expert_names, methodologies, etc
    full_text: str

def parse_md_to_ast(md_text: str) -> OrderAST:
    """
    Parse markdown using state machine:
    - Extract headers (## Case Name, ### Background, etc)
    - Identify blockquotes (> quoted text)
    - Parse case citations (regex: \d{4} WL \d+, \d+ F\.\d+d \d+)
    - Extract entities (names in bold, ALL CAPS parties)
    """
```

**Key Regex Patterns:**
- Case citations: `r'(\d{4}\s+WL\s+\d+)|(\d+\s+F\.\d+d\s+\d+)'`
- Expert names: `r'Dr\.\s+[A-Z][a-z]+|[A-Z][a-z]+,\s+Ph\.?D\.?'`
- Daubert mentions: `r'\bDaubert\b|\bKumho\b|\breliability\b'`

#### Stage 2: Basic Metadata Extraction
**File:** `services/metadata_extractor.py`

Quick extraction for context (no LLM needed):
```python
def extract_basic_metadata(ast: OrderAST) -> dict:
    return {
        'case_name': ast.case_name,
        'date': ast.date or extract_date_from_text(ast.full_text),
        'docket_number': ast.docket_number or extract_docket(ast.full_text),
        'expert_names': ast.entities.get('expert_names', []),
        'citations_count': len(ast.citations),
        'word_count': len(ast.full_text.split()),
        'has_daubert_analysis': 'daubert' in ast.full_text.lower()
    }
```

#### Stage 3: Deep Legal Analysis (GPT-5.1)
**File:** `services/deep_analysis.py`

**Configuration:**
```python
GPT_CONFIG = {
    'model': 'gpt-5.1',
    'temperature': 0.2,  # Low for consistent legal analysis
    'max_tokens': 16000,  # ~2-3 pages of analysis
    'reasoning_effort': 'max',  # Maximum reasoning for complex legal analysis
}
```

**Prompt Engineering:**
```python
DEEP_ANALYSIS_SYSTEM_PROMPT = """You are an expert legal analyst with 20+ years experience in federal civil procedure, expert witness testimony, and Daubert/Kumho standards. You specialize in analyzing judicial patterns for litigation strategy.

Your analysis must be:
- Rigorous: Apply formal legal reasoning, cite specific passages
- Actionable: Provide concrete recommendations for litigators
- Strategic: Identify winning/losing arguments, risks, opportunities
- Precise: Use exact legal terminology, distinguish holding from dicta
"""

DEEP_ANALYSIS_USER_PROMPT = """Analyze this expert witness order from Judge Jane J. Boyle (N.D. Tex.) for a litigator preparing a Daubert motion.

# ORDER TEXT
{full_text}

# EXTRACTED CONTEXT
- Case: {case_name}
- Date: {date}
- Expert(s): {expert_names}
- Word count: {word_count}

# ANALYSIS REQUIREMENTS

Provide comprehensive analysis in 10 structured sections:

## 1. EXECUTIVE SUMMARY (3-4 sentences)
Distill: (a) what happened, (b) why it matters, (c) key takeaway for future cases.

## 2. LEGAL FRAMEWORK APPLIED
- Which Daubert/Kumho factors were central?
- How strictly applied? (cite specific language)
- Fifth Circuit precedent: followed, distinguished, or extended?
- Any novel legal issues addressed?

## 3. JUDGE'S REASONING DEEP DIVE
- Core rationale (with quotes)
- How judge weighed competing arguments
- Logical structure of the opinion
- Unstated assumptions or judicial philosophy evident
- Burden of proof considerations

## 4. EXPERT WITNESS EVALUATION
Break down by Daubert factors:
- **Qualifications**: What credentials mattered? What was insufficient?
- **Methodology**: Reliability assessment, peer review considerations
- **Fit/Relevance**: How judge evaluated connection to case facts
- **Data Sufficiency**: Evidentiary basis requirements

## 5. STRATEGIC IMPLICATIONS FOR LITIGATORS
### If Challenging a Similar Expert:
- Strongest arguments from this order (ranked by effectiveness)
- How to frame methodology attacks
- Qualification weaknesses to highlight
- Procedural timing lessons

### If Defending a Similar Expert:
- Vulnerabilities revealed by this ruling
- Proactive expert qualification strategies
- Evidence gathering priorities (peer review, testing, etc)
- Limiting instruction strategies vs. full exclusion

## 6. RISK FACTORS & RED FLAGS
Pattern recognition:
- Methodological red flags that triggered exclusion
- Qualification gaps (education, experience, specialization)
- Evidentiary deficiencies (lack of testing, no peer review)
- Procedural errors (late disclosure, incomplete reports)
- Expert witness credibility issues

Assign risk levels: 🔴 High (likely exclusion), 🟡 Moderate (partial limitation), 🟢 Low (minimal risk)

## 7. JUDGE BOYLE'S JUDICIAL PATTERNS (Inference)
Based on this order, characterize:
- **Strictness Level**: Lenient / Moderate / Strict (with evidence)
- **Evidentiary Preferences**: Types of evidence judge values most
- **Common Exclusion Grounds**: Ranked by frequency in this opinion
- **Partial vs. Full Exclusion Tendency**: When judge limits vs. excludes entirely
- **Procedural Formalism**: How much process matters to this judge

## 8. PRECEDENT ANALYSIS
For each major case cited:
- Citation + year
- How judge applied it (followed, distinguished, expanded)
- Weight given (central holding vs. passing reference)
- Circuit split considerations
- Binding vs. persuasive authority

## 9. ACTIONABLE RECOMMENDATIONS
### Checklist for Attorneys Preparing Motions Before Judge Boyle:

**DO's** (Priority Actions):
- [ ] [Specific action from this order]
- [ ] [Evidence gathering priority]
- [ ] [Brief writing strategy]

**DON'Ts** (Pitfalls to Avoid):
- [ ] [Argument that failed in this order]
- [ ] [Procedural mistake to avoid]
- [ ] [Overreach that backfired]

**Timing Considerations:**
- Disclosure deadlines
- Motion filing windows
- Supplemental expert report opportunities

## 10. QUOTABLE LANGUAGE FOR BRIEFS
Extract 5-7 key quotes that:
- Capture judge's reasoning succinctly
- Have high citation value in future briefs
- Reveal judicial philosophy on expert testimony
- Can be used by either plaintiff or defense

For each quote:
```json
{
  "quote": "Exact language from order",
  "context": "What issue was being addressed",
  "citation_value": "high|medium|low",
  "useful_for": "challenging_expert|defending_expert|both",
  "legal_principle": "What doctrine/standard it illustrates"
}
```

---

# OUTPUT FORMAT
Return structured JSON matching this schema:

```json
{
  "executive_summary": "string (3-4 sentences)",
  "legal_framework": {
    "daubert_factors_emphasized": ["string"],
    "strictness_level": "lenient|moderate|strict",
    "precedent_treatment": "string",
    "novel_issues": ["string"]
  },
  "reasoning_analysis": {
    "core_rationale": "string (with inline quotes)",
    "argument_weighting": "string",
    "logical_structure": "string",
    "judicial_philosophy": "string"
  },
  "expert_evaluation": {
    "qualifications": {
      "sufficient": ["string"],
      "insufficient": ["string"],
      "critical_credentials": ["string"]
    },
    "methodology": {
      "reliable_aspects": ["string"],
      "unreliable_aspects": ["string"],
      "peer_review_analysis": "string"
    },
    "relevance": "string",
    "data_sufficiency": "string"
  },
  "strategic_implications": {
    "challenging_similar": [
      {"argument": "string", "effectiveness": "high|medium|low"}
    ],
    "defending_similar": [
      {"strategy": "string", "priority": "high|medium|low"}
    ]
  },
  "risk_factors": [
    {
      "factor": "string",
      "risk_level": "high|moderate|low",
      "mitigation": "string"
    }
  ],
  "judge_patterns": {
    "strictness": "lenient|moderate|strict",
    "evidence_preferences": ["string"],
    "common_exclusion_grounds": ["string"],
    "partial_vs_full_tendency": "string",
    "procedural_formalism": "high|medium|low"
  },
  "precedent_analysis": [
    {
      "citation": "string",
      "year": "number",
      "application": "followed|distinguished|expanded",
      "weight": "central|supporting|passing",
      "holding": "string"
    }
  ],
  "recommendations": {
    "dos": ["string"],
    "donts": ["string"],
    "timing": ["string"]
  },
  "key_quotes": [
    {
      "quote": "string",
      "context": "string",
      "citation_value": "high|medium|low",
      "useful_for": "challenging_expert|defending_expert|both",
      "legal_principle": "string"
    }
  ]
}
```

Be specific, cite exact passages, focus on actionable insights that win motions.
"""
```

**Implementation:**
```python
async def generate_deep_analysis(order_data: dict, ast: OrderAST) -> dict:
    """Generate comprehensive legal analysis using GPT-5.1 with max reasoning"""
    
    client = AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY'))
    
    user_prompt = DEEP_ANALYSIS_USER_PROMPT.format(
        full_text=order_data['full_text'],
        case_name=order_data['case_name'],
        date=order_data.get('date', 'Unknown'),
        expert_names=', '.join(order_data.get('expert_names', ['Unknown'])),
        word_count=order_data.get('word_count', 0)
    )
    
    try:
        response = await client.chat.completions.create(
            model='gpt-5.1',
            messages=[
                {'role': 'system', 'content': DEEP_ANALYSIS_SYSTEM_PROMPT},
                {'role': 'user', 'content': user_prompt}
            ],
            temperature=0.2,
            max_tokens=16000,
            reasoning_effort='max',  # Maximum reasoning for complex legal analysis
            response_format={'type': 'json_object'}
        )
        
        analysis = json.loads(response.choices[0].message.content)
        
        # Add metadata
        analysis['_metadata'] = {
            'model': response.model,
            'reasoning_tokens': getattr(response.usage, 'reasoning_tokens', 0),
            'total_tokens': response.usage.total_tokens,
            'timestamp': datetime.utcnow().isoformat(),
            'cost_estimate': calculate_cost(response.usage)
        }
        
        return analysis
        
    except Exception as e:
        logger.error(f"GPT-5.1 analysis failed: {e}")
        raise

def calculate_cost(usage) -> float:
    """Calculate GPT-5.1 cost: $1.25/1M input, $10/1M output"""
    input_cost = (usage.prompt_tokens / 1_000_000) * 1.25
    output_cost = (usage.completion_tokens / 1_000_000) * 10.00
    return round(input_cost + output_cost, 4)
```

#### Stage 4: Embedding Generation
**File:** `services/embeddings.py`

```python
from sentence_transformers import SentenceTransformer

class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.dimension = 384
    
    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for text"""
        return self.model.encode(text, convert_to_numpy=True).tolist()
    
    def embed_order(self, order: dict, analysis: dict) -> dict:
        """Generate embeddings for order and analysis chunks"""
        
        # Full order embedding
        order_embedding = self.embed_text(order['full_text'])
        
        # Analysis chunk embeddings
        chunks = []
        for section_name in ['reasoning_analysis', 'strategic_implications', 
                              'risk_factors', 'recommendations']:
            if section_name in analysis:
                content = json.dumps(analysis[section_name]) if isinstance(
                    analysis[section_name], dict) else str(analysis[section_name])
                
                chunks.append({
                    'section_name': section_name,
                    'content': content,
                    'embedding': self.embed_text(content)
                })
        
        return {
            'order_embedding': order_embedding,
            'analysis_chunks': chunks
        }
```

#### Stage 5: Database Storage
**File:** `db/database.py`

**Schema:**
```sql
-- Core orders table
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_name TEXT NOT NULL,
    docket_number TEXT,
    date TEXT,
    pdf_filename TEXT,
    
    -- Basic metadata
    expert_name TEXT,
    expert_field TEXT,
    ruling_type TEXT,
    exclusion_grounds TEXT,  -- JSON array
    
    -- Content
    full_text TEXT NOT NULL,
    structured_ast TEXT NOT NULL,  -- JSON OrderAST
    
    -- Deep analysis (GPT-5.1 generated)
    deep_analysis TEXT NOT NULL,  -- JSON structured analysis
    analysis_metadata TEXT,  -- Cost, tokens, timestamp
    
    -- Derived fields
    one_line_summary TEXT,
    key_quotes TEXT,  -- JSON array
    precedents_cited TEXT,  -- JSON array
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- FTS5 for full-text search
CREATE VIRTUAL TABLE IF NOT EXISTS orders_fts USING fts5(
    case_name,
    expert_field,
    expert_name,
    full_text,
    content='orders',
    tokenize='porter unicode61'
);

-- Triggers to keep FTS5 in sync
CREATE TRIGGER IF NOT EXISTS orders_fts_insert AFTER INSERT ON orders BEGIN
    INSERT INTO orders_fts(rowid, case_name, expert_field, expert_name, full_text)
    VALUES (new.id, new.case_name, new.expert_field, new.expert_name, new.full_text);
END;

-- Vector embeddings for orders
CREATE VIRTUAL TABLE IF NOT EXISTS order_embeddings USING vec0(
    order_id INTEGER PRIMARY KEY,
    embedding FLOAT[384]
);

-- Analysis chunks for granular RAG
CREATE TABLE IF NOT EXISTS analysis_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    section_name TEXT NOT NULL,
    content TEXT NOT NULL,
    FOREIGN KEY(order_id) REFERENCES orders(id)
);

CREATE VIRTUAL TABLE IF NOT EXISTS chunk_embeddings USING vec0(
    chunk_id INTEGER PRIMARY KEY,
    embedding FLOAT[384]
);
```

**Database Service:**
```python
class DatabaseService:
    def __init__(self, db_path: str = 'data/orders.db'):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()
    
    def insert_order(self, metadata: dict, ast: OrderAST, 
                     analysis: dict, embeddings: dict) -> int:
        """Insert order with all associated data"""
        
        cursor = self.conn.cursor()
        
        # Insert order
        cursor.execute("""
            INSERT INTO orders (
                case_name, docket_number, date, pdf_filename,
                expert_name, expert_field, ruling_type, exclusion_grounds,
                full_text, structured_ast, deep_analysis, analysis_metadata,
                one_line_summary, key_quotes, precedents_cited
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            metadata['case_name'],
            metadata.get('docket_number'),
            metadata.get('date'),
            metadata.get('pdf_filename'),
            metadata.get('expert_name'),
            metadata.get('expert_field'),
            metadata.get('ruling_type'),
            json.dumps(metadata.get('exclusion_grounds', [])),
            ast.full_text,
            json.dumps(asdict(ast)),
            json.dumps(analysis),
            json.dumps(analysis.get('_metadata', {})),
            analysis.get('executive_summary', '')[:200],
            json.dumps(analysis.get('key_quotes', [])),
            json.dumps(ast.citations)
        ))
        
        order_id = cursor.lastrowid
        
        # Insert order embedding
        cursor.execute(
            "INSERT INTO order_embeddings VALUES (?, ?)",
            (order_id, json.dumps(embeddings['order_embedding']))
        )
        
        # Insert analysis chunks
        for chunk in embeddings['analysis_chunks']:
            cursor.execute("""
                INSERT INTO analysis_chunks (order_id, section_name, content)
                VALUES (?, ?, ?)
            """, (order_id, chunk['section_name'], chunk['content']))
            
            chunk_id = cursor.lastrowid
            cursor.execute(
                "INSERT INTO chunk_embeddings VALUES (?, ?)",
                (chunk_id, json.dumps(chunk['embedding']))
            )
        
        self.conn.commit()
        return order_id
```

### 2.3 Parallel Processing Pipeline
**File:** `scripts/process_all_orders.py`

```python
import asyncio
from pathlib import Path

async def process_single_order(
    md_file: Path,
    db: DatabaseService,
    embedding_service: EmbeddingService,
    semaphore: asyncio.Semaphore
) -> dict:
    """Process one order through the full pipeline"""
    
    async with semaphore:  # Rate limit GPT-5.1 calls
        logger.info(f"Processing {md_file.name}...")
        
        # Stage 1: Parse MD → AST
        md_text = md_file.read_text(encoding='utf-8')
        ast = parse_md_to_ast(md_text)
        
        # Stage 2: Extract basic metadata
        metadata = extract_basic_metadata(ast)
        metadata['pdf_filename'] = md_file.name.replace('.md', '.pdf')
        
        # Stage 3: Deep analysis with GPT-5.1 (SLOWEST STEP)
        logger.info(f"🧠 Generating GPT-5.1 analysis for {metadata['case_name']}")
        analysis = await generate_deep_analysis({
            'full_text': ast.full_text,
            'case_name': metadata['case_name'],
            **metadata
        }, ast)
        
        # Stage 4: Generate embeddings
        logger.info(f"📊 Generating embeddings...")
        embeddings = embedding_service.embed_order(
            {'full_text': ast.full_text},
            analysis
        )
        
        # Stage 5: Store in database
        order_id = db.insert_order(metadata, ast, analysis, embeddings)
        
        logger.info(f"✅ Order {order_id}: {metadata['case_name']} "
                   f"({analysis['_metadata']['total_tokens']} tokens, "
                   f"${analysis['_metadata']['cost_estimate']})")
        
        return {
            'order_id': order_id,
            'case_name': metadata['case_name'],
            'tokens': analysis['_metadata']['total_tokens'],
            'cost': analysis['_metadata']['cost_estimate']
        }

async def process_all_orders():
    """Process all 19 orders with parallel GPT-5.1 calls"""
    
    md_files = list(Path('/mnt/user-data/uploads/md_data').glob('*.md'))
    logger.info(f"Found {len(md_files)} orders to process")
    
    db = DatabaseService()
    embedding_service = EmbeddingService()
    
    # Limit to 3 concurrent GPT-5.1 calls (rate limit consideration)
    semaphore = asyncio.Semaphore(3)
    
    start_time = time.time()
    
    results = await asyncio.gather(*[
        process_single_order(md_file, db, embedding_service, semaphore)
        for md_file in md_files
    ])
    
    elapsed = time.time() - start_time
    total_cost = sum(r['cost'] for r in results)
    total_tokens = sum(r['tokens'] for r in results)
    
    logger.info(f"""
    ✅ Processing Complete!
    - Orders processed: {len(results)}
    - Time elapsed: {elapsed:.1f}s
    - Total tokens: {total_tokens:,}
    - Total cost: ${total_cost:.2f}
    - Avg tokens/order: {total_tokens // len(results):,}
    """)

if __name__ == '__main__':
    asyncio.run(process_all_orders())
```

**Expected Output:**
```
Processing 01 - Ameristar Jet Charter Inc v Signal Composites Inc.md...
🧠 Generating GPT-5.1 analysis for Ameristar Jet Charter Inc v Signal Composites Inc
📊 Generating embeddings...
✅ Order 1: Ameristar Jet Charter Inc v Signal Composites Inc (12,450 tokens, $0.135)
...
✅ Processing Complete!
- Orders processed: 19
- Time elapsed: 420.3s (7 minutes)
- Total tokens: 234,567
- Total cost: $2.48
- Avg tokens/order: 12,345
```

---

## 3. FastAPI Backend

### 3.1 Project Structure
```
backend/
├── main.py              # FastAPI app + CORS
├── api/
│   ├── __init__.py
│   ├── routes.py        # All endpoints
│   └── models.py        # Pydantic request/response models
├── services/
│   ├── __init__.py
│   ├── parser.py        # MD → AST
│   ├── metadata_extractor.py
│   ├── deep_analysis.py # GPT-5.1 integration
│   ├── embeddings.py    # Sentence transformers
│   └── search.py        # FTS5 + RAG search
├── db/
│   ├── __init__.py
│   ├── database.py      # SQLite service
│   └── queries.py       # SQL query builders
├── scripts/
│   └── process_all_orders.py
├── data/
│   └── orders.db        # Generated SQLite DB
├── requirements.txt
└── .env                 # OPENAI_API_KEY
```

### 3.2 Core Implementation
**File:** `main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router
import logging

logging.basicConfig(level=logging.INFO)

app = FastAPI(
    title="Know Your Judge - Expert Witness API",
    version="1.0.0",
    description="Backend for analyzing Judge Boyle's expert witness rulings"
)

# CORS for Vite dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 3.3 Search Services
**File:** `services/search.py`

```python
class SearchService:
    def __init__(self, db: DatabaseService, embedding_service: EmbeddingService):
        self.db = db
        self.embedding_service = embedding_service
    
    def keyword_search(self, query: str, limit: int = 10) -> List[dict]:
        """FTS5 full-text search"""
        cursor = self.db.conn.cursor()
        
        # Use FTS5 MATCH with ranking
        results = cursor.execute("""
            SELECT 
                orders.id,
                orders.case_name,
                orders.expert_name,
                orders.expert_field,
                orders.ruling_type,
                orders.one_line_summary,
                snippet(orders_fts, 3, '<mark>', '</mark>', '...', 64) as snippet,
                rank
            FROM orders_fts
            JOIN orders ON orders.id = orders_fts.rowid
            WHERE orders_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """, (query, limit)).fetchall()
        
        return [dict(row) for row in results]
    
    async def semantic_search(self, query: str, limit: int = 10) -> List[dict]:
        """RAG semantic search across orders and analysis"""
        
        # Generate query embedding
        query_embedding = self.embedding_service.embed_text(query)
        
        # Search order embeddings
        order_results = self._vector_similarity_search(
            'order_embeddings',
            query_embedding,
            limit * 2  # Get more candidates
        )
        
        # Search analysis chunks
        chunk_results = self._vector_similarity_search(
            'chunk_embeddings',
            query_embedding,
            limit * 2
        )
        
        # Merge and re-rank
        merged = self._merge_results(order_results, chunk_results, limit)
        
        # Enrich with analysis insights
        enriched = []
        for result in merged:
            order = self.db.get_order(result['order_id'])
            analysis = json.loads(order['deep_analysis'])
            
            enriched.append({
                'order_id': order['id'],
                'case_name': order['case_name'],
                'expert_name': order['expert_name'],
                'expert_field': order['expert_field'],
                'similarity_score': result['similarity'],
                'matched_content': result['content'],
                'analysis_insight': self._extract_relevant_insight(analysis, query),
                'strategic_tips': analysis['recommendations']['dos'][:2],
                'risk_alerts': [r['factor'] for r in analysis['risk_factors'][:2]]
            })
        
        return enriched
    
    def _vector_similarity_search(self, table: str, query_emb: List[float], 
                                   limit: int) -> List[dict]:
        """Cosine similarity search using sqlite-vec"""
        cursor = self.db.conn.cursor()
        
        # Use vec_search (syntax depends on sqlite-vec version)
        results = cursor.execute(f"""
            SELECT 
                {table.replace('_embeddings', '')}_id,
                embedding,
                vec_distance_cosine(embedding, ?) as distance
            FROM {table}
            ORDER BY distance
            LIMIT ?
        """, (json.dumps(query_emb), limit)).fetchall()
        
        return [{
            'order_id': row[0],
            'similarity': 1 - row[2],  # Convert distance to similarity
            'content': self._get_content_for_id(row[0], table)
        } for row in results]
```

---

## 4. API Endpoints (Summary)

See **PRD-3-API-Contract.md** for full OpenAPI specification.

**Core Endpoints:**
- `GET /api/stats` - Dashboard statistics
- `GET /api/orders` - List orders with pagination
- `GET /api/orders/{id}` - Full order detail with analysis
- `POST /api/search/keyword` - FTS5 search
- `POST /api/search/semantic` - RAG search
- `GET /api/insights` - Cross-order pattern synthesis

---

## 5. Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Order processing | <45 min for 19 orders | End-to-end pipeline |
| GPT-5.1 latency | <30s per order | API call time |
| Keyword search | <100ms | FTS5 query |
| Semantic search | <500ms | Embedding + vector search |
| API response time | <200ms avg | All endpoints |

---

## 6. Error Handling & Logging

```python
# Logging configuration
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('logs/processing.log')
handler.setFormatter(logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
))
logger.addHandler(handler)

# Error handling
class ProcessingError(Exception):
    """Base exception for processing errors"""
    pass

class GPTAnalysisError(ProcessingError):
    """GPT-5.1 analysis failed"""
    pass

class EmbeddingError(ProcessingError):
    """Embedding generation failed"""
    pass

# Retry logic for GPT-5.1
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
async def generate_deep_analysis_with_retry(*args, **kwargs):
    return await generate_deep_analysis(*args, **kwargs)
```

---

## 7. Cost Estimation

**GPT-5.1 Pricing:**
- Input: $1.25 per 1M tokens
- Output: $10.00 per 1M tokens

**Expected Usage (19 orders):**
- Input: ~2,000 tokens/order × 19 = 38,000 tokens → $0.05
- Output: ~12,000 tokens/order × 19 = 228,000 tokens → $2.28
- **Total: ~$2.33** (plus reasoning tokens, likely ~$3-4 total)

**Infrastructure:**
- SQLite: Free
- sentence-transformers: Free (local)
- FastAPI: Free

---

## 8. Testing Strategy

```python
# tests/test_pipeline.py
import pytest

@pytest.mark.asyncio
async def test_process_single_order():
    """Test full pipeline on one order"""
    md_file = Path('test_data/sample_order.md')
    result = await process_single_order(md_file, ...)
    
    assert result['order_id'] > 0
    assert 'cost' in result
    assert result['tokens'] > 1000

def test_keyword_search():
    """Test FTS5 search"""
    results = search_service.keyword_search('Daubert methodology')
    
    assert len(results) > 0
    assert 'snippet' in results[0]
    assert '<mark>' in results[0]['snippet']

@pytest.mark.asyncio
async def test_semantic_search():
    """Test RAG search"""
    results = await search_service.semantic_search(
        'medical expert excluded for future damages'
    )
    
    assert len(results) > 0
    assert results[0]['similarity_score'] > 0.5
```

---

## 9. Deployment

**Local Development:**
```bash
# Setup
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Process orders
python scripts/process_all_orders.py

# Run server
uvicorn main:app --reload --port 8000
```

**Environment Variables:**
```bash
OPENAI_API_KEY=sk-...
DATABASE_PATH=data/orders.db
LOG_LEVEL=INFO
```

---

## 10. Success Metrics

- ✅ All 19 orders processed successfully
- ✅ Deep analysis quality validated (manual spot-check of 3 orders)
- ✅ Search latency under targets
- ✅ Total cost under $5
- ✅ API endpoints functional with frontend integration
- ✅ Zero data loss or corruption

---

## Appendix A: Dependencies

**requirements.txt:**
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
pydantic==2.5.0
python-dotenv==1.0.0
openai==1.3.0
sentence-transformers==2.2.2
sqlite-vec==0.0.1  # Requires compilation
tenacity==8.2.3
pytest==7.4.3
pytest-asyncio==0.21.1
```

---

**End of Backend PRD**
