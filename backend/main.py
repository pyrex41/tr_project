"""
FastAPI Backend for Legal Orders Analysis

Main application entry point with CORS, routes, and error handling.
"""

import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pathlib import Path

from backend.db.database import DatabaseService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global database service
db_service: DatabaseService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown."""
    global db_service

    # Startup
    logger.info("Starting Legal Analysis API...")
    db_service = DatabaseService()
    logger.info("Database service initialized")

    yield

    # Shutdown
    logger.info("Shutting down Legal Analysis API...")


# Create FastAPI app
app = FastAPI(
    title="Legal Analysis API",
    description="API for analyzing Judge Boyle's expert witness rulings",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative dev port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        stats = db_service.get_stats()
        return {
            "status": "healthy",
            "database": "connected",
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "error": str(e)}
        )


# Database statistics
@app.get("/api/stats")
async def get_stats():
    """Get database statistics."""
    try:
        stats = db_service.get_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Get all orders
@app.get("/api/orders")
async def get_orders(limit: int = 100, offset: int = 0):
    """
    Get all orders with pagination.

    Args:
        limit: Maximum number of results (default: 100)
        offset: Number of results to skip (default: 0)
    """
    try:
        orders = db_service.get_all_orders(limit=limit, offset=offset)
        return {
            "success": True,
            "count": len(orders),
            "data": orders
        }
    except Exception as e:
        logger.error(f"Error getting orders: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Get single order by ID
@app.get("/api/orders/{order_id}")
async def get_order(order_id: int):
    """
    Get a single order by ID.

    Args:
        order_id: Order ID
    """
    try:
        order = db_service.get_order_by_id(order_id)
        if not order:
            raise HTTPException(status_code=404, detail=f"Order {order_id} not found")

        return {
            "success": True,
            "data": order
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting order {order_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Keyword search
@app.get("/api/search/keyword")
async def keyword_search(q: str, limit: int = 10):
    """
    Perform FTS5 keyword search.

    Args:
        q: Search query
        limit: Maximum results (default: 10)
    """
    try:
        if not q or len(q.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query parameter 'q' is required")

        results = db_service.keyword_search(q, limit=limit)
        return {
            "success": True,
            "query": q,
            "count": len(results),
            "data": results
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in keyword search: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Legal Analysis API",
        "version": "1.0.0",
        "description": "API for analyzing Judge Boyle's expert witness rulings",
        "endpoints": {
            "health": "/health",
            "stats": "/api/stats",
            "orders": "/api/orders",
            "order_by_id": "/api/orders/{id}",
            "keyword_search": "/api/search/keyword?q=query"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
