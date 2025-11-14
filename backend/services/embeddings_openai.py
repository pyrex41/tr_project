"""
OpenAI Embeddings Service

Uses OpenAI's Embeddings API instead of local sentence-transformers.
This eliminates the need for PyTorch and large model files in production.
"""

import logging
import os
from typing import List
import numpy as np
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)


class OpenAIEmbeddingService:
    """
    Embedding service using OpenAI's text-embedding-3-small model.

    Much lighter than sentence-transformers - no PyTorch required!
    """

    def __init__(self, model: str = "text-embedding-3-small", dimensions: int = 384):
        """
        Initialize OpenAI embedding service.

        Args:
            model: OpenAI embedding model (text-embedding-3-small or text-embedding-3-large)
            dimensions: Output dimensions (384 to match existing embeddings)
        """
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.dimensions = dimensions
        logger.info(f"OpenAI embedding service initialized (model={model}, dimensions={dimensions})")

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    def generate_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for text using OpenAI API.

        Args:
            text: Input text to embed

        Returns:
            384-dimensional numpy array (normalized)
        """
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text,
                dimensions=self.dimensions  # Match existing embeddings
            )

            embedding = np.array(response.data[0].embedding, dtype=np.float32)

            # Normalize to unit length (for cosine similarity)
            norm = np.linalg.norm(embedding)
            if norm > 0:
                embedding = embedding / norm

            return embedding

        except Exception as e:
            logger.error(f"Error generating OpenAI embedding: {e}")
            raise

    def generate_embeddings_batch(self, texts: List[str]) -> List[np.ndarray]:
        """
        Generate embeddings for multiple texts (batch processing).

        Args:
            texts: List of input texts

        Returns:
            List of 384-dimensional numpy arrays
        """
        try:
            # OpenAI supports batch embedding (up to 2048 texts)
            response = self.client.embeddings.create(
                model=self.model,
                input=texts,
                dimensions=self.dimensions
            )

            embeddings = []
            for data in response.data:
                embedding = np.array(data.embedding, dtype=np.float32)

                # Normalize
                norm = np.linalg.norm(embedding)
                if norm > 0:
                    embedding = embedding / norm

                embeddings.append(embedding)

            return embeddings

        except Exception as e:
            logger.error(f"Error generating OpenAI embeddings batch: {e}")
            raise
