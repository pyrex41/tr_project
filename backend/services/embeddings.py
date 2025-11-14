"""
Embeddings Generation Service

Generates 384-dimensional vectors using sentence-transformers.
"""

import logging
from typing import List
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for generating embeddings using sentence-transformers."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize embedding service.

        Args:
            model_name: Name of the sentence-transformers model
        """
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.dimensions = 384  # all-MiniLM-L6-v2 produces 384-dim vectors
        logger.info(f"Embedding model loaded. Dimensions: {self.dimensions}")

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text

        Returns:
            384-dimensional embedding vector as list of floats
        """
        if not text or len(text.strip()) == 0:
            logger.warning("Empty text provided for embedding")
            return [0.0] * self.dimensions

        try:
            # Generate embedding
            embedding = self.model.encode(text, convert_to_tensor=False)

            # Convert to list of floats and normalize
            embedding_list = embedding.tolist()

            # L2 normalization for cosine similarity
            norm = np.linalg.norm(embedding_list)
            if norm > 0:
                embedding_list = (np.array(embedding_list) / norm).tolist()

            return embedding_list

        except Exception as e:
            logger.error(f"Error generating embedding: {e}", exc_info=True)
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts in batch.

        Args:
            texts: List of input texts

        Returns:
            List of 384-dimensional embedding vectors
        """
        if not texts:
            return []

        try:
            # Filter out empty texts
            valid_texts = [text if text and len(text.strip()) > 0 else " " for text in texts]

            # Generate embeddings in batch
            embeddings = self.model.encode(valid_texts, convert_to_tensor=False, show_progress_bar=True)

            # Convert to list and normalize
            embeddings_list = []
            for embedding in embeddings:
                embedding_arr = np.array(embedding)
                norm = np.linalg.norm(embedding_arr)
                if norm > 0:
                    embedding_arr = embedding_arr / norm
                embeddings_list.append(embedding_arr.tolist())

            return embeddings_list

        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}", exc_info=True)
            raise

    def get_dimensions(self) -> int:
        """Get the dimensionality of embeddings."""
        return self.dimensions
