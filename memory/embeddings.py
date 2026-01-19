import numpy as np
from sentence_transformers import SentenceTransformer
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("NexusEmbeddings")

class NexusEmbeddings:
    """
    Handles text-to-vector conversion using a local SentenceTransformer model.
    Optimized for CPU usage.
    """
    def __init__(self, model_name="all-MiniLM-L6-v2"):
        logger.info(f"Loading embedding model: {model_name}...")
        try:
            self.model = SentenceTransformer(model_name)
            logger.info("Embedding model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise e

    def embed(self, text: str) -> np.ndarray:
        """
        Converts a single string to a numpy vector.
        """
        if not text:
            return np.zeros(384, dtype='float32') # Fallback for empty text
            
        vector = self.model.encode(text)
        return np.array(vector, dtype='float32')

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        """
        Converts a list of strings to a matrix of vectors.
        """
        if not texts:
            return np.array([], dtype='float32')
            
        vectors = self.model.encode(texts)
        return np.array(vectors, dtype='float32')

# Singleton instance for easy import
try:
    embedding_model = NexusEmbeddings()
except Exception as e:
    logger.error("Could not initialize global embedding model.")
    embedding_model = None
