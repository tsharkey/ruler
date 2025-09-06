#!/usr/bin/env python3
"""
Search rules using semantic similarity
"""

import psycopg2
from sentence_transformers import SentenceTransformer
import sys

# Database configuration - UPDATE THESE
DB_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres', 
    'password': 'postgres',
    'port': 5432
}

def search_rules(query_text, limit=5):
    """Search for similar rules using text query"""
    print(f"Searching for rules similar to: '{query_text}'")
    
    # Load model
    print("Loading model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Generate embedding for query
    query_embedding = model.encode([query_text])[0]
    
    # Connect to database
    conn = psycopg2.connect(**DB_CONFIG)
    
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
    
    conn.close()
    
    # Display results
    print(f"\nTop {limit} similar rules:")
    print("=" * 80)
    
    if not results:
        print("No results found. Make sure embeddings have been created.")
        return
    
    for i, (rule_id, rule_text, game_name, similarity) in enumerate(results, 1):
        print(f"{i}. Rule ID: {rule_id} | Game: {game_name or 'N/A'} | Similarity: {similarity:.3f}")
        print(f"   Rule: {rule_text}")
        print("-" * 80)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print('  python3 search-rules.py "your search query"')
        print('  python3 search-rules.py "player movement" 10  # with custom limit')
        print("\nExamples:")
        print('  python3 search-rules.py "how to win"')
        print('  python3 search-rules.py "dice rolling"')
        print('  python3 search-rules.py "player movement"')
        return
    
    query = sys.argv[1]
    limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    
    search_rules(query, limit)

if __name__ == "__main__":
    main()
