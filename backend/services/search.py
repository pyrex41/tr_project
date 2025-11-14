"""
Search Services

Combines FTS5 keyword search with vector semantic search for comprehensive retrieval.
"""

import logging
import struct
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

from db.database import DatabaseService
from services.embeddings import EmbeddingService

logger = logging.getLogger(__name__)


class SearchService:
    """Service for hybrid search combining keyword and semantic search."""

    def __init__(self, db_service: DatabaseService, embedding_service: EmbeddingService):
        """
        Initialize search service.

        Args:
            db_service: Database service instance
            embedding_service: Embedding service instance
        """
        self.db = db_service
        self.embedding_service = embedding_service
        logger.info("Search service initialized")

    def keyword_search(
        self,
        query: str,
        limit: int = 10,
        min_score: Optional[float] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform FTS5 keyword search.

        Args:
            query: Search query string
            limit: Maximum number of results
            min_score: Minimum relevance score threshold

        Returns:
            List of matching orders with metadata and scores
        """
        logger.info(f"Keyword search: '{query}' (limit={limit})")

        results = self.db.keyword_search(query, limit=limit)

        # Filter by minimum score if specified
        if min_score is not None:
            results = [r for r in results if r['relevance_score'] >= min_score]

        logger.info(f"Found {len(results)} keyword search results")
        return results

    def semantic_search(
        self,
        query: str,
        limit: int = 10,
        search_type: str = "order"
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic vector search.

        Args:
            query: Search query string
            limit: Maximum number of results
            search_type: "order" for full orders, "chunk" for analysis sections

        Returns:
            List of matching results with similarity scores
        """
        logger.info(f"Semantic search: '{query}' (type={search_type}, limit={limit})")

        # Generate embedding for query
        query_embedding = self.embedding_service.generate_embedding(query)

        if search_type == "order":
            results = self._search_order_embeddings(query_embedding, limit)
        elif search_type == "chunk":
            results = self._search_chunk_embeddings(query_embedding, limit)
        else:
            raise ValueError(f"Invalid search_type: {search_type}")

        logger.info(f"Found {len(results)} semantic search results")
        return results

    def _search_order_embeddings(
        self,
        query_embedding: List[float],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search order embeddings using cosine similarity."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Get all order embeddings
            cursor.execute("""
                SELECT oe.order_id, oe.embedding, o.filename, o.metadata_json
                FROM order_embeddings oe
                JOIN orders o ON oe.order_id = o.id
            """)

            results = []
            query_vec = np.array(query_embedding)

            for row in cursor.fetchall():
                order_id = row['order_id']
                embedding_bytes = row['embedding']
                filename = row['filename']
                metadata_json = row['metadata_json']

                # Deserialize embedding
                embedding = struct.unpack(f'{len(embedding_bytes)//4}f', embedding_bytes)
                embedding_vec = np.array(embedding)

                # Calculate cosine similarity
                similarity = float(np.dot(query_vec, embedding_vec))

                results.append({
                    'order_id': order_id,
                    'filename': filename,
                    'metadata': self.db._parse_json(metadata_json),
                    'similarity_score': similarity
                })

            # Sort by similarity (descending)
            results.sort(key=lambda x: x['similarity_score'], reverse=True)

            return results[:limit]

    def _search_chunk_embeddings(
        self,
        query_embedding: List[float],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Search analysis chunk embeddings using cosine similarity."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Get all chunk embeddings with order info
            cursor.execute("""
                SELECT
                    ce.chunk_id,
                    ce.embedding,
                    ac.order_id,
                    ac.section_name,
                    ac.content,
                    o.filename,
                    o.metadata_json
                FROM chunk_embeddings ce
                JOIN analysis_chunks ac ON ce.chunk_id = ac.id
                JOIN orders o ON ac.order_id = o.id
            """)

            results = []
            query_vec = np.array(query_embedding)

            for row in cursor.fetchall():
                chunk_id = row['chunk_id']
                embedding_bytes = row['embedding']
                order_id = row['order_id']
                section_name = row['section_name']
                content = row['content']
                filename = row['filename']
                metadata_json = row['metadata_json']

                # Deserialize embedding
                embedding = struct.unpack(f'{len(embedding_bytes)//4}f', embedding_bytes)
                embedding_vec = np.array(embedding)

                # Calculate cosine similarity
                similarity = float(np.dot(query_vec, embedding_vec))

                results.append({
                    'chunk_id': chunk_id,
                    'order_id': order_id,
                    'filename': filename,
                    'section_name': section_name,
                    'content': content[:500] + '...' if len(content) > 500 else content,
                    'metadata': self.db._parse_json(metadata_json),
                    'similarity_score': similarity
                })

            # Sort by similarity (descending)
            results.sort(key=lambda x: x['similarity_score'], reverse=True)

            return results[:limit]

    def hybrid_search(
        self,
        query: str,
        limit: int = 10,
        keyword_weight: float = 0.3,
        semantic_weight: float = 0.7
    ) -> List[Dict[str, Any]]:
        """
        Perform hybrid search combining keyword and semantic search.

        Args:
            query: Search query string
            limit: Maximum number of results
            keyword_weight: Weight for keyword search scores (0-1)
            semantic_weight: Weight for semantic search scores (0-1)

        Returns:
            List of results with combined scores
        """
        logger.info(f"Hybrid search: '{query}' (kw={keyword_weight}, sem={semantic_weight})")

        # Normalize weights
        total_weight = keyword_weight + semantic_weight
        keyword_weight = keyword_weight / total_weight
        semantic_weight = semantic_weight / total_weight

        # Perform both searches
        keyword_results = self.keyword_search(query, limit=limit * 2)
        semantic_results = self.semantic_search(query, limit=limit * 2, search_type="order")

        # Combine results by order_id
        combined_scores = {}

        # Add keyword scores (normalize BM25 scores)
        keyword_scores = [r['relevance_score'] for r in keyword_results]
        if keyword_scores:
            min_score = min(keyword_scores)
            max_score = max(keyword_scores)
            score_range = max_score - min_score if max_score != min_score else 1

            for result in keyword_results:
                order_id = result['id']
                normalized_score = (result['relevance_score'] - min_score) / score_range
                combined_scores[order_id] = {
                    'keyword_score': normalized_score * keyword_weight,
                    'semantic_score': 0,
                    'result': result
                }

        # Add semantic scores (already normalized 0-1)
        for result in semantic_results:
            order_id = result['order_id']
            semantic_score = result['similarity_score'] * semantic_weight

            if order_id in combined_scores:
                combined_scores[order_id]['semantic_score'] = semantic_score
            else:
                # Get order details
                order = self.db.get_order_by_id(order_id)
                if order:
                    combined_scores[order_id] = {
                        'keyword_score': 0,
                        'semantic_score': semantic_score,
                        'result': {
                            'id': order_id,
                            'filename': order['filename'],
                            'metadata': order['metadata']
                        }
                    }

        # Calculate final scores and sort
        final_results = []
        for order_id, scores in combined_scores.items():
            final_score = scores['keyword_score'] + scores['semantic_score']
            result = scores['result']
            result['hybrid_score'] = final_score
            result['keyword_score'] = scores['keyword_score']
            result['semantic_score'] = scores['semantic_score']
            final_results.append(result)

        # Sort by hybrid score
        final_results.sort(key=lambda x: x['hybrid_score'], reverse=True)

        logger.info(f"Hybrid search returned {len(final_results[:limit])} results")
        return final_results[:limit]


# Helper method for DatabaseService
def _parse_json(self, json_str: str) -> Any:
    """Parse JSON string."""
    import json
    return json.loads(json_str) if json_str else None


# Monkey patch the helper method
DatabaseService._parse_json = _parse_json
