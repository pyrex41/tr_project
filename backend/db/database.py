"""
Database Service for Legal Orders

SQLite database with:
- FTS5 full-text search
- sqlite-vec for vector embeddings
- 5 tables: orders, orders_fts, order_embeddings, analysis_chunks, chunk_embeddings
"""

import sqlite3
import json
import logging
import struct
from pathlib import Path
from typing import Dict, Any, List, Optional
from contextlib import contextmanager
import sqlite_vec

logger = logging.getLogger(__name__)


class DatabaseService:
    """Service for managing legal orders database."""

    def __init__(self, db_path: str = "data/orders.db"):
        """
        Initialize database service.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        # Initialize database schema
        self._initialize_schema()
        logger.info(f"Database initialized at: {self.db_path}")

    @contextmanager
    def get_connection(self):
        """Get database connection with sqlite-vec loaded."""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.enable_load_extension(True)
        sqlite_vec.load(conn)
        conn.enable_load_extension(False)
        try:
            yield conn
        finally:
            conn.close()

    def _initialize_schema(self):
        """Initialize database schema with all tables and triggers."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Table 1: Main orders table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename TEXT UNIQUE NOT NULL,
                    raw_text TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    analysis_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Table 2: FTS5 full-text search table
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS orders_fts USING fts5(
                    filename,
                    raw_text,
                    analysis_text,
                    content='orders',
                    content_rowid='id'
                )
            """)

            # Table 3: Order embeddings (384-dimensional vectors)
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS order_embeddings USING vec0(
                    order_id INTEGER PRIMARY KEY,
                    embedding FLOAT[384]
                )
            """)

            # Table 4: Analysis chunk storage
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS analysis_chunks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    section_name TEXT NOT NULL,
                    content TEXT NOT NULL,
                    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE
                )
            """)

            # Table 5: Chunk embeddings
            cursor.execute("""
                CREATE VIRTUAL TABLE IF NOT EXISTS chunk_embeddings USING vec0(
                    chunk_id INTEGER PRIMARY KEY,
                    embedding FLOAT[384]
                )
            """)

            # Trigger 1: Insert into FTS5 when order is inserted
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS orders_ai AFTER INSERT ON orders BEGIN
                    INSERT INTO orders_fts(rowid, filename, raw_text, analysis_text)
                    VALUES (
                        new.id,
                        new.filename,
                        new.raw_text,
                        COALESCE(json_extract(new.analysis_json, '$.analysis.case_context') || ' ' ||
                                 json_extract(new.analysis_json, '$.analysis.court_reasoning') || ' ' ||
                                 json_extract(new.analysis_json, '$.analysis.key_takeaways'), '')
                    );
                END
            """)

            # Trigger 2: Update FTS5 when order is updated
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS orders_au AFTER UPDATE ON orders BEGIN
                    UPDATE orders_fts
                    SET filename = new.filename,
                        raw_text = new.raw_text,
                        analysis_text = COALESCE(
                            json_extract(new.analysis_json, '$.analysis.case_context') || ' ' ||
                            json_extract(new.analysis_json, '$.analysis.court_reasoning') || ' ' ||
                            json_extract(new.analysis_json, '$.analysis.key_takeaways'), ''
                        )
                    WHERE rowid = new.id;
                END
            """)

            # Trigger 3: Delete from FTS5 when order is deleted
            cursor.execute("""
                CREATE TRIGGER IF NOT EXISTS orders_ad AFTER DELETE ON orders BEGIN
                    DELETE FROM orders_fts WHERE rowid = old.id;
                END
            """)

            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_orders_filename ON orders(filename)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_chunks_order_id ON analysis_chunks(order_id)
            """)

            conn.commit()
            logger.info("Database schema initialized successfully")

    def insert_order(
        self,
        filename: str,
        raw_text: str,
        metadata: Dict[str, Any],
        analysis: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Insert a new order into the database.

        Args:
            filename: Original filename
            raw_text: Full text of the order
            metadata: Extracted metadata dictionary
            analysis: Optional deep analysis dictionary

        Returns:
            Order ID (rowid)
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO orders (filename, raw_text, metadata_json, analysis_json)
                VALUES (?, ?, ?, ?)
            """, (
                filename,
                raw_text,
                json.dumps(metadata),
                json.dumps(analysis) if analysis else None
            ))

            order_id = cursor.lastrowid
            conn.commit()

            logger.info(f"Inserted order: {filename} (ID: {order_id})")
            return order_id

    def update_analysis(self, order_id: int, analysis: Dict[str, Any]) -> None:
        """
        Update the analysis for an existing order.

        Args:
            order_id: Order ID
            analysis: Analysis dictionary to update
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE orders
                SET analysis_json = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (json.dumps(analysis), order_id))

            conn.commit()
            logger.info(f"Updated analysis for order ID: {order_id}")

    def insert_order_embedding(self, order_id: int, embedding: List[float]) -> None:
        """
        Insert embedding for an order.

        Args:
            order_id: Order ID
            embedding: 384-dimensional embedding vector
        """
        if len(embedding) != 384:
            raise ValueError(f"Embedding must be 384-dimensional, got {len(embedding)}")

        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Serialize embedding as little-endian float32 bytes
            embedding_bytes = struct.pack(f'{len(embedding)}f', *embedding)

            cursor.execute("""
                INSERT INTO order_embeddings (order_id, embedding)
                VALUES (?, ?)
            """, (order_id, embedding_bytes))

            conn.commit()
            logger.info(f"Inserted embedding for order ID: {order_id}")

    def insert_analysis_chunk(
        self,
        order_id: int,
        section_name: str,
        content: str,
        embedding: Optional[List[float]] = None
    ) -> int:
        """
        Insert an analysis chunk with optional embedding.

        Args:
            order_id: Order ID
            section_name: Name of the analysis section
            content: Chunk content
            embedding: Optional 384-dimensional embedding

        Returns:
            Chunk ID
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Insert chunk
            cursor.execute("""
                INSERT INTO analysis_chunks (order_id, section_name, content)
                VALUES (?, ?, ?)
            """, (order_id, section_name, content))

            chunk_id = cursor.lastrowid

            # Insert embedding if provided
            if embedding:
                if len(embedding) != 384:
                    raise ValueError(f"Embedding must be 384-dimensional, got {len(embedding)}")

                # Serialize embedding as little-endian float32 bytes
                embedding_bytes = struct.pack(f'{len(embedding)}f', *embedding)
                cursor.execute("""
                    INSERT INTO chunk_embeddings (chunk_id, embedding)
                    VALUES (?, ?)
                """, (chunk_id, embedding_bytes))

            conn.commit()
            logger.info(f"Inserted chunk for order {order_id}: {section_name}")
            return chunk_id

    def get_order_by_id(self, order_id: int) -> Optional[Dict[str, Any]]:
        """
        Get an order by ID.

        Args:
            order_id: Order ID

        Returns:
            Order dictionary or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, filename, raw_text, metadata_json, analysis_json, created_at, updated_at
                FROM orders
                WHERE id = ?
            """, (order_id,))

            row = cursor.fetchone()
            if not row:
                return None

            return {
                'id': row['id'],
                'filename': row['filename'],
                'raw_text': row['raw_text'],
                'metadata': json.loads(row['metadata_json']),
                'analysis': json.loads(row['analysis_json']) if row['analysis_json'] else None,
                'created_at': row['created_at'],
                'updated_at': row['updated_at']
            }

    def get_all_orders(self, limit: int = 100, offset: int = 0, include_analysis: bool = False) -> List[Dict[str, Any]]:
        """
        Get all orders with pagination.

        Args:
            limit: Maximum number of results
            offset: Number of results to skip
            include_analysis: Whether to include analysis_json in response

        Returns:
            List of order dictionaries
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            if include_analysis:
                cursor.execute("""
                    SELECT id, filename, metadata_json, analysis_json, created_at
                    FROM orders
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))
            else:
                cursor.execute("""
                    SELECT id, filename, metadata_json, created_at
                    FROM orders
                    ORDER BY created_at DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))

            rows = cursor.fetchall()
            result = []
            for row in rows:
                order_dict = {
                    'id': row['id'],
                    'filename': row['filename'],
                    'metadata': json.loads(row['metadata_json']),
                    'created_at': row['created_at']
                }
                if include_analysis and 'analysis_json' in row.keys():
                    order_dict['analysis'] = json.loads(row['analysis_json']) if row['analysis_json'] else None
                result.append(order_dict)

            return result

    def keyword_search(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Perform FTS5 keyword search.

        Args:
            query: Search query
            limit: Maximum results

        Returns:
            List of matching orders with relevance scores
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    o.id,
                    o.filename,
                    o.metadata_json,
                    o.raw_text,
                    bm25(orders_fts) as relevance_score
                FROM orders_fts
                JOIN orders o ON orders_fts.order_id = o.id
                WHERE orders_fts MATCH ?
                ORDER BY relevance_score
                LIMIT ?
            """, (query, limit))

            rows = cursor.fetchall()
            return [
                {
                    'id': row['id'],
                    'filename': row['filename'],
                    'metadata': json.loads(row['metadata_json']),
                    'raw_text': row['raw_text'],
                    'relevance_score': row['relevance_score']
                }
                for row in rows
            ]

    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics.

        Returns:
            Statistics dictionary
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()

            stats = {}

            # Count orders
            cursor.execute("SELECT COUNT(*) as count FROM orders")
            stats['total_orders'] = cursor.fetchone()['count']

            # Count with analysis
            cursor.execute("SELECT COUNT(*) as count FROM orders WHERE analysis_json IS NOT NULL")
            stats['orders_with_analysis'] = cursor.fetchone()['count']

            # Count embeddings
            cursor.execute("SELECT COUNT(*) as count FROM order_embeddings")
            stats['order_embeddings'] = cursor.fetchone()['count']

            # Count chunks
            cursor.execute("SELECT COUNT(*) as count FROM analysis_chunks")
            stats['analysis_chunks'] = cursor.fetchone()['count']

            # Count chunk embeddings
            cursor.execute("SELECT COUNT(*) as count FROM chunk_embeddings")
            stats['chunk_embeddings'] = cursor.fetchone()['count']

            return stats
