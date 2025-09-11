"""
RAG service for searching board game rules
"""

import psycopg2
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any
import os
from functools import lru_cache

# Database configuration - consider moving to config later
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'), 
    'password': os.getenv('DB_PASSWORD', 'postgres'),
    'port': int(os.getenv('DB_PORT', 5432))
}

class RAGService:
    def __init__(self):
        self.model = None
        self._load_model()
    
    @lru_cache(maxsize=1)
    def _load_model(self):
        """Load sentence transformer model (cached)"""
        if self.model is None:
            print("Loading sentence transformer model...")
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        return self.model
    
    def search_rules(self, query_text: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Search for similar rules using text query"""
        
        # Generate embedding for query
        model = self._load_model()
        query_embedding = model.encode([query_text])[0]
        
        # Connect to database and search
        conn = psycopg2.connect(**DB_CONFIG)
        
        try:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT 
                        r.id,
                        r.rule,
                        g.name as game_name,
                        1 - (r.embedding <=> %s::vector) as similarity
                    FROM rules r
                    LEFT JOIN games g ON r.game_id = g.id
                    WHERE r.embedding IS NOT NULL
                    ORDER BY r.embedding <=> %s::vector
                    LIMIT %s
                """, (query_embedding.tolist(), query_embedding.tolist(), limit))
                
                results = cur.fetchall()
        finally:
            conn.close()
        
        # Format results
        formatted_results = []
        for rule_id, rule_text, game_name, similarity in results:
            formatted_results.append({
                "id": rule_id,
                "rule": rule_text,
                "game_name": game_name or "Unknown",
                "similarity": round(similarity, 3)
            })
        
        return formatted_results

# Create singleton instance
rag_service = RAGService()
