# PRD: API Contract Specification
## Know Your Judge - Expert Witness Analysis

**Version:** 1.0  
**Date:** November 14, 2025  
**Owner:** Engineering Team  
**Timeline:** 3 hours (POC phase)

---

## 1. Overview

### 1.1 Purpose
Define the REST API contract between the FastAPI backend and Elm frontend for the Know Your Judge POC. This document serves as the single source of truth for API endpoints, request/response formats, error handling, and data models.

### 1.2 API Design Principles
- **RESTful**: Follow REST conventions for resource naming and HTTP methods
- **JSON**: All payloads use JSON encoding
- **Typed**: Strong typing with Pydantic (backend) and Elm decoders (frontend)
- **Consistent**: Uniform response structures across all endpoints
- **Fast**: Target <200ms response time for all endpoints

### 1.3 Base URL
```
Development: http://localhost:8000/api
Production: TBD
```

### 1.4 Authentication
Not required for POC (single-user demo).

---

## 2. Common Data Models

### 2.1 Standard Response Envelope

All responses follow this structure:

```typescript
// Success response
{
  "data": <T>,           // Response payload (type varies by endpoint)
  "meta"?: {             // Optional metadata
    "timestamp": "ISO8601 datetime",
    "version": "1.0.0"
  }
}

// Error response (HTTP 4xx/5xx)
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details"?: {}       // Optional additional context
  }
}
```

### 2.2 Core Types

#### Stats
```typescript
{
  "total_orders": number,
  "grant_rate": number,              // 0.0-1.0
  "top_expert_type": string | null,
  "partial_count": number,
  "rulings": {
    "granted": number,
    "denied": number,
    "partial": number
  },
  "expert_types": {
    [type: string]: number           // e.g., {"medical": 8, "financial": 4}
  },
  "common_grounds": Array<{
    "ground": string,
    "count": number
  }>
}
```

**Pydantic Model:**
```python
class Stats(BaseModel):
    total_orders: int
    grant_rate: float
    top_expert_type: Optional[str]
    partial_count: int
    rulings: Dict[str, int]
    expert_types: Dict[str, int]
    common_grounds: List[Dict[str, Any]]
```

**Elm Type:**
```elm
type alias Stats =
    { totalOrders : Int
    , grantRate : Float
    , topExpertType : Maybe String
    , partialCount : Int
    , rulings : Dict String Int
    , expertTypes : Dict String Int
    , commonGrounds : List { ground : String, count : Int }
    }
```

#### SearchResult
```typescript
{
  "order_id": number,
  "case_name": string,
  "expert_name": string,
  "expert_field": string,
  "ruling_type": "granted" | "denied" | "partial" | "limited",
  "snippet": string,                 // HTML with <mark> tags
  "relevance_score": number,         // 0.0-1.0
  "analysis_insight"?: string,       // For semantic search
  "strategic_tips"?: string[],
  "risk_alerts"?: string[]
}
```

**Pydantic Model:**
```python
class SearchResult(BaseModel):
    order_id: int
    case_name: str
    expert_name: str
    expert_field: str
    ruling_type: str
    snippet: str
    relevance_score: float
    analysis_insight: Optional[str] = None
    strategic_tips: Optional[List[str]] = None
    risk_alerts: Optional[List[str]] = None
```

**Elm Type:**
```elm
type alias SearchResult =
    { orderId : Int
    , caseName : String
    , expertName : String
    , expertField : String
    , rulingType : String
    , snippet : String
    , relevanceScore : Float
    , analysisInsight : Maybe String
    , strategicTips : Maybe (List String)
    , riskAlerts : Maybe (List String)
    }
```

#### OrderSummary (for list views)
```typescript
{
  "id": number,
  "case_name": string,
  "date": string,                    // ISO8601 date
  "expert_name": string,
  "expert_field": string,
  "ruling_type": "granted" | "denied" | "partial" | "limited",
  "one_line_summary": string
}
```

#### OrderDetail (full order)
```typescript
{
  "id": number,
  "case_name": string,
  "docket_number": string,
  "date": string,
  "expert_name": string,
  "expert_field": string,
  "ruling_type": string,
  "full_text": string,
  "structured_ast": {...},           // JSON AST representation
  "deep_analysis": {
    "executive_summary": string,
    "legal_framework": {
      "daubert_factors_emphasized": string[],
      "strictness_level": "lenient" | "moderate" | "strict",
      "precedent_treatment": string,
      "novel_issues": string[]
    },
    "reasoning_analysis": {
      "core_rationale": string,
      "argument_weighting": string,
      "logical_structure": string,
      "judicial_philosophy": string
    },
    "expert_evaluation": {
      "qualifications": {
        "sufficient": string[],
        "insufficient": string[],
        "critical_credentials": string[]
      },
      "methodology": {
        "reliable_aspects": string[],
        "unreliable_aspects": string[],
        "peer_review_analysis": string
      },
      "relevance": string,
      "data_sufficiency": string
    },
    "strategic_implications": {
      "challenging_similar": Array<{
        "argument": string,
        "effectiveness": "high" | "medium" | "low"
      }>,
      "defending_similar": Array<{
        "strategy": string,
        "priority": "high" | "medium" | "low"
      }>
    },
    "risk_factors": Array<{
      "factor": string,
      "risk_level": "high" | "moderate" | "low",
      "mitigation": string
    }>,
    "judge_patterns": {
      "strictness": string,
      "evidence_preferences": string[],
      "common_exclusion_grounds": string[],
      "partial_vs_full_tendency": string,
      "procedural_formalism": "high" | "medium" | "low"
    },
    "precedent_analysis": Array<{
      "citation": string,
      "year": number,
      "application": "followed" | "distinguished" | "expanded",
      "weight": "central" | "supporting" | "passing",
      "holding": string
    }>,
    "recommendations": {
      "dos": string[],
      "donts": string[],
      "timing": string[]
    },
    "key_quotes": Array<{
      "quote": string,
      "context": string,
      "citation_value": "high" | "medium" | "low",
      "useful_for": "challenging_expert" | "defending_expert" | "both",
      "legal_principle": string
    }>
  },
  "analysis_metadata": {
    "model": string,
    "reasoning_tokens": number,
    "total_tokens": number,
    "cost_estimate": number,
    "timestamp": string
  }
}
```

#### Insight
```typescript
{
  "type": "warning" | "success" | "info",
  "description": string,
  "evidence": number[],              // Array of order IDs
  "confidence": number,              // 0-100
  "strength": "strong" | "moderate" | "weak"
}
```

---

## 3. Endpoint Specifications

### 3.1 GET /api/health

**Purpose:** Health check endpoint

**Request:**
```http
GET /api/health
```

**Response:** `200 OK`
```json
{
  "status": "healthy",
  "timestamp": "2025-11-14T09:00:00Z",
  "version": "1.0.0"
}
```

**Errors:** None

---

### 3.2 GET /api/stats

**Purpose:** Retrieve dashboard statistics

**Request:**
```http
GET /api/stats
```

**Response:** `200 OK`
```json
{
  "total_orders": 19,
  "grant_rate": 0.63,
  "top_expert_type": "medical",
  "partial_count": 2,
  "rulings": {
    "granted": 12,
    "denied": 5,
    "partial": 2
  },
  "expert_types": {
    "medical": 8,
    "financial": 4,
    "fire_investigation": 2,
    "other": 5
  },
  "common_grounds": [
    {"ground": "unreliable_methodology", "count": 8},
    {"ground": "not_qualified", "count": 5},
    {"ground": "irrelevant", "count": 3}
  ]
}
```

**Errors:**
- `500 Internal Server Error` - Database error

**Implementation:**
```python
@app.get("/api/stats", response_model=Stats)
async def get_stats():
    """Get dashboard statistics"""
    db = DatabaseService()
    
    total_orders = db.count_orders()
    rulings = db.count_by_ruling_type()
    expert_types = db.count_by_expert_field()
    
    granted = rulings.get('granted', 0)
    total = sum(rulings.values())
    grant_rate = granted / total if total > 0 else 0.0
    
    return Stats(
        total_orders=total_orders,
        grant_rate=grant_rate,
        top_expert_type=max(expert_types, key=expert_types.get) if expert_types else None,
        partial_count=rulings.get('partial', 0),
        rulings=rulings,
        expert_types=expert_types,
        common_grounds=db.get_common_grounds()
    )
```

---

### 3.3 GET /api/orders

**Purpose:** List orders with pagination and filtering

**Request:**
```http
GET /api/orders?limit=20&offset=0&ruling_type=granted&expert_field=medical
```

**Query Parameters:**
- `limit` (optional, default=20): Number of results per page
- `offset` (optional, default=0): Pagination offset
- `ruling_type` (optional): Filter by ruling type
- `expert_field` (optional): Filter by expert field
- `sort_by` (optional, default=date): Sort field (date, case_name)
- `sort_order` (optional, default=desc): Sort order (asc, desc)

**Response:** `200 OK`
```json
{
  "items": [
    {
      "id": 9,
      "case_name": "Hanan v. Crete Carrier Corp.",
      "date": "2020-01-31",
      "expert_name": "Dr. Bhat",
      "expert_field": "medical",
      "ruling_type": "granted",
      "one_line_summary": "Excluded medical expert testimony on future medical expenses"
    }
  ],
  "total": 19,
  "limit": 20,
  "offset": 0
}
```

**Errors:**
- `400 Bad Request` - Invalid query parameters
- `500 Internal Server Error` - Database error

**Implementation:**
```python
@app.get("/api/orders", response_model=OrderListResponse)
async def get_orders(
    limit: int = 20,
    offset: int = 0,
    ruling_type: Optional[str] = None,
    expert_field: Optional[str] = None,
    sort_by: str = "date",
    sort_order: str = "desc"
):
    """List orders with filtering and pagination"""
    db = DatabaseService()
    
    filters = {}
    if ruling_type:
        filters['ruling_type'] = ruling_type
    if expert_field:
        filters['expert_field'] = expert_field
    
    orders = db.get_orders(
        limit=limit,
        offset=offset,
        filters=filters,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    total = db.count_orders(filters=filters)
    
    return OrderListResponse(
        items=orders,
        total=total,
        limit=limit,
        offset=offset
    )
```

---

### 3.4 GET /api/orders/{order_id}

**Purpose:** Get full order detail including deep analysis

**Request:**
```http
GET /api/orders/9
```

**Path Parameters:**
- `order_id` (required): Order ID

**Response:** `200 OK`
```json
{
  "id": 9,
  "case_name": "Hanan v. Crete Carrier Corp.",
  "docket_number": "3:18-CV-2780-G",
  "date": "2020-01-31",
  "expert_name": "Dr. Bhat",
  "expert_field": "medical",
  "ruling_type": "granted",
  "full_text": "...",
  "structured_ast": {...},
  "deep_analysis": {
    "executive_summary": "...",
    "legal_framework": {...},
    ...
  },
  "analysis_metadata": {
    "model": "gpt-5.1",
    "total_tokens": 12450,
    "cost_estimate": 0.135,
    "timestamp": "2025-11-14T08:30:00Z"
  }
}
```

**Errors:**
- `404 Not Found` - Order ID does not exist
- `500 Internal Server Error` - Database error

**Implementation:**
```python
@app.get("/api/orders/{order_id}", response_model=OrderDetail)
async def get_order_detail(order_id: int):
    """Get full order detail with analysis"""
    db = DatabaseService()
    
    order = db.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return order
```

---

### 3.5 POST /api/search/keyword

**Purpose:** Full-text keyword search using FTS5

**Request:**
```http
POST /api/search/keyword
Content-Type: application/json

{
  "query": "daubert methodology",
  "limit": 10,
  "filters": {
    "ruling_type": "granted",
    "expert_field": "medical"
  }
}
```

**Request Body:**
- `query` (required): Search query string
- `limit` (optional, default=10): Max results
- `filters` (optional): Additional filters

**Response:** `200 OK`
```json
[
  {
    "order_id": 9,
    "case_name": "Hanan v. Crete Carrier Corp.",
    "expert_name": "Dr. Bhat",
    "expert_field": "medical",
    "ruling_type": "granted",
    "snippet": "...reliable <mark>methodology</mark> under <mark>Daubert</mark>...",
    "relevance_score": 0.85
  }
]
```

**Errors:**
- `400 Bad Request` - Empty query
- `500 Internal Server Error` - Search error

**Implementation:**
```python
@app.post("/api/search/keyword", response_model=List[SearchResult])
async def keyword_search(request: KeywordSearchRequest):
    """FTS5 keyword search"""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    search_service = SearchService()
    results = search_service.keyword_search(
        query=request.query,
        limit=request.limit,
        filters=request.filters
    )
    
    return results
```

---

### 3.6 POST /api/search/semantic

**Purpose:** Semantic/RAG search using vector embeddings

**Request:**
```http
POST /api/search/semantic
Content-Type: application/json

{
  "query": "medical expert testimony on future damages",
  "limit": 10
}
```

**Request Body:**
- `query` (required): Natural language search query
- `limit` (optional, default=10): Max results

**Response:** `200 OK`
```json
[
  {
    "order_id": 9,
    "case_name": "Hanan v. Crete Carrier Corp.",
    "expert_name": "Dr. Bhat",
    "expert_field": "medical",
    "ruling_type": "granted",
    "snippet": "...",
    "relevance_score": 0.92,
    "analysis_insight": "Judge emphasized lack of specific knowledge about plaintiff's condition",
    "strategic_tips": [
      "Ensure expert has case-specific expertise",
      "Provide peer-reviewed support for methodology"
    ],
    "risk_alerts": [
      "Generic expertise insufficient",
      "Future damages require strong factual foundation"
    ]
  }
]
```

**Errors:**
- `400 Bad Request` - Empty query
- `500 Internal Server Error` - Embedding/search error

**Implementation:**
```python
@app.post("/api/search/semantic", response_model=List[SearchResult])
async def semantic_search(request: SemanticSearchRequest):
    """Semantic RAG search"""
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    
    search_service = SearchService()
    results = await search_service.semantic_search(
        query=request.query,
        limit=request.limit
    )
    
    return results
```

---

### 3.7 GET /api/insights

**Purpose:** Get AI-generated cross-order insights

**Request:**
```http
GET /api/insights
```

**Response:** `200 OK`
```json
{
  "insights": [
    {
      "type": "warning",
      "description": "Judge requires peer-reviewed methodology for novel medical techniques",
      "evidence": [1, 3, 7, 9],
      "confidence": 80,
      "strength": "strong"
    },
    {
      "type": "success",
      "description": "Fire investigators using NFPA standards rarely excluded",
      "evidence": [8, 12],
      "confidence": 65,
      "strength": "moderate"
    },
    {
      "type": "info",
      "description": "Partial exclusions more common for damages experts than medical experts",
      "evidence": [6, 11, 14],
      "confidence": 70,
      "strength": "moderate"
    }
  ]
}
```

**Errors:**
- `500 Internal Server Error` - Analysis error

**Implementation:**
```python
@app.get("/api/insights", response_model=InsightsResponse)
async def get_insights():
    """Get AI-generated cross-order insights"""
    db = DatabaseService()
    
    # Retrieve all analyses
    analyses = db.get_all_analyses()
    
    # Generate insights (cached or compute)
    insights = generate_cross_order_insights(analyses)
    
    return InsightsResponse(insights=insights)
```

---

## 4. Error Handling

### 4.1 Error Response Format

All errors follow this structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable description",
    "details": {...}
  }
}
```

### 4.2 HTTP Status Codes

- `200 OK` - Successful request
- `400 Bad Request` - Invalid input (validation error)
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side error
- `503 Service Unavailable` - Temporary service disruption

### 4.3 Error Codes

- `VALIDATION_ERROR` - Request validation failed
- `NOT_FOUND` - Resource does not exist
- `DATABASE_ERROR` - Database query failed
- `SEARCH_ERROR` - Search operation failed
- `ANALYSIS_ERROR` - GPT-5.1 analysis failed

### 4.4 Example Error Responses

**404 Not Found:**
```json
{
  "error": {
    "code": "NOT_FOUND",
    "message": "Order with ID 999 does not exist"
  }
}
```

**400 Bad Request:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters",
    "details": {
      "limit": ["Must be between 1 and 100"]
    }
  }
}
```

**500 Internal Server Error:**
```json
{
  "error": {
    "code": "DATABASE_ERROR",
    "message": "Failed to query database"
  }
}
```

---

## 5. API Versioning

### 5.1 Version Strategy
- Version embedded in URL path: `/api/v1/...`
- For POC, unversioned `/api/...` is acceptable
- Production should use `/api/v1/...`

### 5.2 Deprecation
When endpoints change:
1. Mark old endpoint as deprecated in docs
2. Add `X-API-Deprecation-Date` header
3. Maintain old endpoint for 90 days
4. Return migration guide in response

---

## 6. Performance Targets

| Endpoint | Target Latency | Max Latency |
|----------|----------------|-------------|
| GET /api/stats | < 50ms | 100ms |
| GET /api/orders | < 100ms | 200ms |
| GET /api/orders/{id} | < 150ms | 300ms |
| POST /api/search/keyword | < 100ms | 200ms |
| POST /api/search/semantic | < 500ms | 1000ms |
| GET /api/insights | < 200ms | 500ms |

---

## 7. Rate Limiting

Not implemented for POC. Production should implement:
- 100 requests/minute per IP
- 1000 requests/hour per IP
- Return `429 Too Many Requests` when exceeded

---

## 8. CORS Configuration

**Allowed Origins (Development):**
- `http://localhost:5173` (Vite dev server)

**Allowed Methods:**
- GET, POST, OPTIONS

**Allowed Headers:**
- Content-Type, Authorization

**FastAPI Configuration:**
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 9. Testing

### 9.1 Unit Tests
Test each endpoint with pytest:

```python
def test_get_stats(client):
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_orders" in data
    assert data["total_orders"] == 19

def test_keyword_search_empty_query(client):
    response = client.post("/api/search/keyword", json={"query": ""})
    assert response.status_code == 400
    assert "error" in response.json()
```

### 9.2 Integration Tests
Test full workflow:

```python
@pytest.mark.asyncio
async def test_search_to_detail_workflow(client):
    # 1. Search
    search_response = client.post("/api/search/keyword", json={
        "query": "daubert"
    })
    assert search_response.status_code == 200
    results = search_response.json()
    assert len(results) > 0
    
    # 2. Get detail
    order_id = results[0]["order_id"]
    detail_response = client.get(f"/api/orders/{order_id}")
    assert detail_response.status_code == 200
    assert "deep_analysis" in detail_response.json()
```

### 9.3 Load Tests
Use Locust or Apache Bench:

```bash
# Test search endpoint
ab -n 1000 -c 10 -p search_payload.json -T application/json \
   http://localhost:8000/api/search/keyword
```

---

## 10. Documentation

### 10.1 OpenAPI/Swagger

FastAPI automatically generates OpenAPI docs at:
- Interactive docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

### 10.2 Postman Collection

Export OpenAPI spec and import to Postman for manual testing.

---

## 11. Example Request/Response Flows

### 11.1 Dashboard Load Flow

```
1. Frontend loads
   GET /api/stats
   → Returns: Stats object
   
   GET /api/insights
   → Returns: List of insights

2. Render dashboard with charts
```

### 11.2 Search Flow

```
1. User types "daubert methodology"
   POST /api/search/keyword
   {
     "query": "daubert methodology",
     "limit": 10
   }
   → Returns: List of SearchResult objects

2. User clicks result
   GET /api/orders/9
   → Returns: Full OrderDetail with analysis

3. User switches to semantic search
   POST /api/search/semantic
   {
     "query": "daubert methodology",
     "limit": 10
   }
   → Returns: SearchResult objects with analysis insights
```

### 11.3 Order Detail Flow

```
1. Navigate to order detail page
   GET /api/orders/9
   → Returns: OrderDetail with full analysis

2. View different tabs (no additional API calls needed)
   - Full text, analysis, citations all in initial response

3. Copy quote (client-side only, no API call)
```

---

## 12. Security Considerations

### 12.1 Input Validation
- Sanitize all user inputs
- Limit query string length (max 500 chars)
- Validate order IDs are integers
- Prevent SQL injection (use parameterized queries)

### 12.2 Rate Limiting
Implement in production to prevent abuse.

### 12.3 HTTPS
Use HTTPS in production (not required for local POC).

---

## 13. Monitoring & Logging

### 13.1 Access Logs
Log all API requests:
```
2025-11-14 09:00:00 | GET /api/stats | 200 | 45ms | 192.168.1.1
2025-11-14 09:00:01 | POST /api/search/keyword | 200 | 120ms | 192.168.1.1
```

### 13.2 Error Logs
Log all errors with stack traces:
```
2025-11-14 09:00:02 | ERROR | Database connection failed
Traceback: ...
```

### 13.3 Metrics
Track:
- Request count by endpoint
- Average response time
- Error rate
- Search query distribution

---

## 14. Deployment Checklist

- [ ] Environment variables configured (OPENAI_API_KEY, etc.)
- [ ] Database initialized with processed orders
- [ ] CORS origins set correctly
- [ ] Error handling tested
- [ ] API docs accessible
- [ ] Performance benchmarks met
- [ ] Frontend integration tested

---

## Appendix A: Complete Type Definitions

### Python (Pydantic)

```python
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class Stats(BaseModel):
    total_orders: int
    grant_rate: float
    top_expert_type: Optional[str]
    partial_count: int
    rulings: Dict[str, int]
    expert_types: Dict[str, int]
    common_grounds: List[Dict[str, Any]]

class OrderSummary(BaseModel):
    id: int
    case_name: str
    date: str
    expert_name: str
    expert_field: str
    ruling_type: str
    one_line_summary: str

class SearchResult(BaseModel):
    order_id: int
    case_name: str
    expert_name: str
    expert_field: str
    ruling_type: str
    snippet: str
    relevance_score: float
    analysis_insight: Optional[str] = None
    strategic_tips: Optional[List[str]] = None
    risk_alerts: Optional[List[str]] = None

class KeywordSearchRequest(BaseModel):
    query: str
    limit: int = 10
    filters: Optional[Dict[str, str]] = None

class SemanticSearchRequest(BaseModel):
    query: str
    limit: int = 10

class Insight(BaseModel):
    type: str  # warning, success, info
    description: str
    evidence: List[int]  # order IDs
    confidence: int  # 0-100
    strength: str  # strong, moderate, weak

class InsightsResponse(BaseModel):
    insights: List[Insight]

# ... (OrderDetail, Analysis, etc. - see Backend PRD for full definitions)
```

### Elm

```elm
-- Types.elm
module Types exposing (..)

import Dict exposing (Dict)

type alias Stats =
    { totalOrders : Int
    , grantRate : Float
    , topExpertType : Maybe String
    , partialCount : Int
    , rulings : Dict String Int
    , expertTypes : Dict String Int
    , commonGrounds : List CommonGround
    }

type alias CommonGround =
    { ground : String
    , count : Int
    }

type alias SearchResult =
    { orderId : Int
    , caseName : String
    , expertName : String
    , expertField : String
    , rulingType : String
    , snippet : String
    , relevanceScore : Float
    , analysisInsight : Maybe String
    , strategicTips : Maybe (List String)
    , riskAlerts : Maybe (List String)
    }

type alias Insight =
    { type_ : String
    , description : String
    , evidence : List Int
    , confidence : Int
    , strength : String
    }

-- ... (OrderDetail, Analysis, etc.)
```

---

**End of API Contract PRD**
