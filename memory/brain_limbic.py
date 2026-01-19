import faiss
import duckdb
import numpy as np
import time
import json
import os
from .embeddings import embedding_model

class NexusMemory:
    """
    The Hippocampus of Nexus.
    Manages Long-Term Memory (LTM) using FAISS (Vector Store) and DuckDB (Metadata Store).
    """
    def __init__(self, memory_dir="memory"):
        self.memory_dir = memory_dir
        os.makedirs(memory_dir, exist_ok=True)
        
        # 1. Initialize Vector Store (FAISS)
        # 384 dimensions for all-MiniLM-L6-v2
        self.dimension = 384 
        self.index_path = os.path.join(memory_dir, "episodic.index")
        
        if os.path.exists(self.index_path):
            self.index = faiss.read_index(self.index_path)
        else:
            self.index = faiss.IndexFlatL2(self.dimension)
            
        # 2. Initialize Metadata Store (DuckDB)
        self.db_path = os.path.join(memory_dir, "metadata.duckdb")
        self.conn = duckdb.connect(self.db_path)
        self._init_db()
        
    def _init_db(self):
        """Create schema if not exists"""
        self.conn.execute("""
            CREATE SEQUENCE IF NOT EXISTS seq_memory_id START 1;
            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY DEFAULT nextval('seq_memory_id'),
                content TEXT,
                type TEXT, -- 'episodic', 'semantic', 'fact'
                timestamp DOUBLE,
                importance DOUBLE, -- 0.0 to 1.0 (Salience)
                access_count INTEGER DEFAULT 0,
                last_accessed DOUBLE
            )
        """)
        
    def add_memory(self, content: str, type="episodic", importance=0.5):
        """
        Encodes content and stores in both FAISS (Vector) and DuckDB (Metadata).
        """
        if not content:
            return
            
        # 1. Vectorize
        vector = embedding_model.embed(content)
        
        # 2. Store in FAISS
        # FAISS add returns nothing, so we assume sequential ID matching with DuckDB
        # CRITICAL: We need strict ID alignment. 
        # For simplicity in V1: We trust DuckDB ID = FAISS Index ID + 1 (since SQL starts at 1, FAISS at 0)
        self.index.add(np.array([vector])) 
        faiss.write_index(self.index, self.index_path)
        
        # 3. Store Metadata
        timestamp = time.time()
        self.conn.execute("""
            INSERT INTO memories (content, type, timestamp, importance, last_accessed)
            VALUES (?, ?, ?, ?, ?)
        """, (content, type, timestamp, importance, timestamp))
        
        return True

    def recall(self, query: str, k=5):
        """
        Retrieves top-k relevant memories based on vector similarity.
        """
        vector = embedding_model.embed(query)
        
        # Search FAISS
        # distances, indices = self.index.search(np.array([vector]), k)
        
        # Robust search even if index is empty
        if self.index.ntotal == 0:
            return []
            
        distances, indices = self.index.search(np.array([vector]), k)
        
        results = []
        for i, idx in enumerate(indices[0]):
            if idx == -1: continue # No result
            
            # Fetch content from DuckDB
            # FAISS Index `idx` maps to DuckDB row (approx strategy: we assume idx matches Nth row inserted)
            # Better strategy: We prefer fetching by content match or storing ID in FAISS (IndexIDMap)
            # For V1: We will rely on row_id offset. 
            # DuckDB Memories are 1-based, FAISS 0-based.
            db_id = int(idx) + 1
            
            row = self.conn.execute("SELECT content, type, importance FROM memories WHERE id = ?", (db_id,)).fetchone()
            if row:
                results.append({
                    "content": row[0],
                    "type": row[1],
                    "importance": row[2],
                    "score": float(distances[0][i])
                })
                
                # Update access stats (Memory Strengthening)
                self.conn.execute("UPDATE memories SET access_count = access_count + 1, last_accessed = ? WHERE id = ?", (time.time(), db_id))
                
        return results

    def forget_trivial(self):
        """
        Prunes memories with low importance and low recall frequency.
        (Implementation planned for Sleep Phase)
        """
        pass
