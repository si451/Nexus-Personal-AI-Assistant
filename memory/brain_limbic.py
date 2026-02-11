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
        Retrieves top-k relevant memories using a Weighted Scoring System:
        Score = Semantic Similarity * Importance Boost * Time Decay
        """
        # 1. Vectorize query
        vector = embedding_model.embed(query)
        if hasattr(vector, "tolist"):
            vector = vector.tolist()
            
        # 2. Build Filter
        where = {}
        if filter_type: where["type"] = filter_type
        if only_creator_memories: where["involves_creator"] = True
            
        # 3. Fetch Candidates (Fetch 3x needed to allow for re-ranking)
        # We fetch more because vector search only gives semantic match, 
        # but we want to promote recent/important ones that might be slightly less semantically close
        n_candidates = k * 4
        results = self.collection.query(
            query_embeddings=[vector],
            n_results=n_candidates,
            where=where if where else None
        )
        
        candidates = []
        current_time = time.time()
        
        if results['ids'] and results['ids'][0]:
            for i, id in enumerate(results['ids'][0]):
                meta = results['metadatas'][0][i]
                dist = results['distances'][0][i]
                base_similarity = 1.0 - (dist / 2) # Cosine distance usually 0-2, normalize roughly
                base_similarity = max(0.1, base_similarity)

                # --- HUMAN-LIKE MEMORY SCORING ---
                
                # A. Importance (0.0 - 1.0)
                importance = meta.get("importance", 0.5)
                
                # B. Recency (Time Decay)
                # Memories fade over time unless valuable
                mem_time = meta.get("timestamp", current_time)
                age_hours = (current_time - mem_time) / 3600
                
                # Decay curve: Fast drop-off, long tail
                # 1 hr = 1.0, 24 hr = 0.8, 1 week = 0.5
                recency_score = 1.0 / (1.0 + (age_hours / 72.0)) 
                
                # C. Significance Override
                # If highly significant (0.9+), ignore decay almost entirely
                significance = meta.get("significance", 0.0)
                if significance > 0.8:
                    recency_score = max(recency_score, 0.9)
                
                # D. Creator Bias
                # Always remember moments with Siddi better
                creator_boost = 1.2 if meta.get("involves_creator") else 1.0
                
                # FINAL SCORE
                final_score = base_similarity * (1 + importance) * recency_score * creator_boost
                
                candidates.append({
                    "id": id,
                    "content": results['documents'][0][i],
                    "metadata": meta,
                    "final_score": final_score,
                    "similarity": base_similarity
                })

        # 4. Sort and Select Top K
        candidates.sort(key=lambda x: x["final_score"], reverse=True)
        top_memories = candidates[:k]
        
        # 5. Format and Update Access Stats (Reinforcement)
        formatted_memories = []
        for mem in top_memories:
            meta = mem["metadata"]
            
            # Formatted Output
            formatted_memories.append({
                "content": mem["content"],
                "type": meta.get("type", "episodic"),
                "importance": meta.get("importance"),
                "emotion": meta.get("emotion"),
                "dist_score": mem["similarity"],
                "final_score": mem["final_score"]
            })
            
            # Memory Consolidation (Reinforcement)
            # Every time we recall it, it becomes stronger (reset decay slightly)
            try:
                meta["access_count"] = meta.get("access_count", 0) + 1
                meta["last_accessed"] = current_time
                # Boost importance slightly on recall (Repetition = Learning)
                meta["importance"] = min(1.0, meta.get("importance", 0.5) + 0.01)
                
                # Update metadata only — do NOT pass embeddings to avoid
                # overwriting the memory's original vector
                self.collection.update(
                    ids=[mem["id"]],
                    metadatas=[meta]
                )
            except Exception as e:
                print(f"[Memory] ⚠️ Failed to update access stats: {e}")
            
        return formatted_memories

    def forget_trivial(self):
        """
        Mimics synaptic pruning. 
        Deletes old, low-importance memories to clear noise.
        """
        current_time = time.time()
        # Get all memories (chunked if massive, but fine for now)
        all_mems = self.collection.get()
        
        ids_to_delete = []
        
        if all_mems['ids']:
            for i, id in enumerate(all_mems['ids']):
                meta = all_mems['metadatas'][i]
                
                importance = meta.get("importance", 0.5)
                significance = meta.get("significance", 0.0)
                mem_time = meta.get("timestamp", current_time)
                age_days = (current_time - mem_time) / 86400
                
                # DELETE CRITERIA:
                # 1. Very old (> 7 days) and very unimportant (< 0.3)
                if age_days > 7 and importance < 0.3 and significance < 0.3:
                    ids_to_delete.append(id)
                # 2. Ancient (> 30 days) and mediocre importance (< 0.5)
                elif age_days > 30 and importance < 0.5 and significance < 0.5:
                    ids_to_delete.append(id)
        
        if ids_to_delete:
            print(f"[Memory] 🧹 Pruning {len(ids_to_delete)} faded memories...")
            self.collection.delete(ids=ids_to_delete)
        else:
            print("[Memory] Brain checks out healthy. No pruning needed.")

    def recall_emotional(self, emotion: str, k: int = 5) -> List[Dict]:
        """Recall memories with a specific emotional tone."""
        results = self.collection.get(
            where={"emotion": emotion},
            limit=k
        )
        return self._format_get_results(results)
    
    def recall_creator_moments(self, k: int = 10) -> List[Dict]:
        """Recall memories involving the creator (Siddi), ranked by relevance."""
        # Use semantic search with creator filter for ranked results
        return self.recall(
            query="My time with Siddi, our shared moments and conversations",
            k=k,
            only_creator_memories=True
        )
    
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
    
    def consolidate_similar(self, similarity_threshold: float = 0.92):
        """
        Merges near-duplicate memories to reduce noise.
        If two memories have cosine similarity > threshold, keeps the more important one.
        """
        all_mems = self.collection.get(include=["embeddings", "metadatas", "documents"])
        
        if not all_mems['ids'] or len(all_mems['ids']) < 2:
            print("[Memory] Not enough memories to consolidate.")
            return
        
        import numpy as np
        ids = all_mems['ids']
        embeddings = np.array(all_mems['embeddings'])
        metadatas = all_mems['metadatas']
        
        # Find duplicates using cosine similarity
        ids_to_delete = set()
        
        for i in range(len(ids)):
            if ids[i] in ids_to_delete:
                continue
            for j in range(i + 1, len(ids)):
                if ids[j] in ids_to_delete:
                    continue
                
                # Cosine similarity
                sim = np.dot(embeddings[i], embeddings[j]) / (
                    np.linalg.norm(embeddings[i]) * np.linalg.norm(embeddings[j]) + 1e-8
                )
                
                if sim > similarity_threshold:
                    # Keep the more important one
                    imp_i = metadatas[i].get("importance", 0.5)
                    imp_j = metadatas[j].get("importance", 0.5)
                    
                    if imp_i >= imp_j:
                        ids_to_delete.add(ids[j])
                    else:
                        ids_to_delete.add(ids[i])
        
        if ids_to_delete:
            print(f"[Memory] 🔗 Consolidating {len(ids_to_delete)} near-duplicate memories...")
            self.collection.delete(ids=list(ids_to_delete))
        else:
            print("[Memory] No duplicates found. Memory is clean.")
