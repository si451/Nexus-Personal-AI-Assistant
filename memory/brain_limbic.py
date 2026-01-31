"""
Nexus Memory: Brain Limbic Module (Vector Edition)
==================================================
The Hippocampus of Nexus.
Now powered by ChromaDB for persistent, efficient vector storage.
"""

import chromadb
import uuid
import time
import os
from datetime import datetime
from typing import List, Dict, Optional
from .embeddings import embedding_model

class NexusMemory:
    """
    The Hippocampus of Nexus.
    Stores memories as vectors in ChromaDB for semantic retrieval.
    """
    
    def __init__(self, memory_dir="data/memory_vector_db"):
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)
        
        # Initialize ChromaDB Client
        self.client = chromadb.PersistentClient(path=memory_dir)
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="nexus_ltm",
            metadata={"hnsw:space": "cosine"}
        )
        
    def add_memory(self, 
                   content: str, 
                   type: str = "episodic", 
                   importance: float = 0.5,
                   emotion: str = "neutral",
                   significance: float = 0.5,
                   involves_creator: bool = False,
                   context: str = ""):
        """
        Stores a memory in the vector database.
        """
        if not content:
            return
        
        # Boost importance heuristics
        if emotion not in ["neutral", ""]:
            importance = min(1.0, importance + 0.1)
        if involves_creator:
            importance = min(1.0, importance + 0.2)
        if significance > 0.7:
            importance = min(1.0, importance + 0.1)
            
        # Generate ID and Timestamp
        mem_id = str(uuid.uuid4())
        timestamp = time.time()
        
        # Vectorize using our centralized model
        vector = embedding_model.embed(content)
        if hasattr(vector, "tolist"):
            vector = vector.tolist()
            
        # Add to Chroma
        self.collection.add(
            ids=[mem_id],
            embeddings=[vector],
            documents=[content],
            metadatas=[{
                "type": type,
                "importance": importance,
                "emotion": emotion,
                "significance": significance,
                "involves_creator": involves_creator,
                "context": context,
                "timestamp": timestamp,
                "access_count": 0,
                "last_accessed": timestamp
            }]
        )
        
        if significance >= 0.7 or involves_creator:
            print(f"[Memory] 💭 Significant memory stored: {content[:50]}...")
            
        return True

    def recall(self, query: str, k: int = 5, 
               filter_type: Optional[str] = None,
               only_creator_memories: bool = False) -> List[Dict]:
        """
        Retrieves top-k relevant memories using semantic search.
        """
        # Vectorize query
        vector = embedding_model.embed(query)
        if hasattr(vector, "tolist"):
            vector = vector.tolist()
            
        # Build Metadata Filter
        where = {}
        if filter_type:
            where["type"] = filter_type
        if only_creator_memories:
            where["involves_creator"] = True
            
        # Query
        results = self.collection.query(
            query_embeddings=[vector],
            n_results=k,
            where=where if where else None
        )
        
        # Format Results
        memories = []
        if results['ids'] and results['ids'][0]:
            for i, id in enumerate(results['ids'][0]):
                meta = results['metadatas'][0][i]
                content = results['documents'][0][i]
                dist = results['distances'][0][i]
                
                memories.append({
                    "content": content,
                    "type": meta.get("type", "episodic"),
                    "importance": meta.get("importance", 0.5),
                    "emotion": meta.get("emotion", "neutral"),
                    "significance": meta.get("significance", 0.5),
                    "involves_creator": meta.get("involves_creator", False),
                    "score": 1.0 - dist # Convert distance to similarity score approx
                })
                
                # Update access count (fire and forget update)
                try:
                    meta["access_count"] += 1
                    meta["last_accessed"] = time.time()
                    self.collection.update(
                        ids=[id],
                        embeddings=[vector], # Re-supplying vector is needed for update usually or at least recommened to avoid re-embed
                        metadatas=[meta]
                    )
                except:
                    pass
                    
        return memories

    def recall_emotional(self, emotion: str, k: int = 5) -> List[Dict]:
        """Recall memories with a specific emotional tone."""
        results = self.collection.get(
            where={"emotion": emotion},
            limit=k
        )
        return self._format_get_results(results)
    
    def recall_creator_moments(self, k: int = 10) -> List[Dict]:
        """Recall memories involving the creator (Siddi)."""
        results = self.collection.get(
            where={"involves_creator": True},
            limit=k
        )
        # Note: .get() doesn't sort by semantic relevance, just returns matching
        # Ideally we'd embed a generic query like "My time with Siddi" if we wanted sort.
        # But this works for pure filtering.
        return self._format_get_results(results)
    
    def _format_get_results(self, results) -> List[Dict]:
        memories = []
        if results['ids']:
            for i, id in enumerate(results['ids']):
                meta = results['metadatas'][i]
                content = results['documents'][i]
                memories.append({
                    "content": content,
                    "type": meta.get("type", "episodic"),
                    "importance": meta.get("importance"),
                    "emotion": meta.get("emotion"),
                    "significance": meta.get("significance"),
                    "involves_creator": meta.get("involves_creator")
                })
        return memories

    def get_memory_stats(self) -> Dict:
        """Get statistics about stored memories."""
        return {
            "total_memories": self.collection.count(),
            "vector_backend": "chromadb"
        }
    
    def consolidate_similar(self):
        pass

    def forget_trivial(self):
        pass
