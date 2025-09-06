#!/usr/bin/env python3
"""
Simple script to generate and store embeddings for rules table
"""

import psycopg2
from sentence_transformers import SentenceTransformer

# Database configuration - UPDATE THESE
DB_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres', 
    'password': 'postgres',
    'port': 5432
}

def main():
    # Load model
    print("Loading sentence transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Connect to database
    print("Connecting to database...")
    conn = psycopg2.connect(**DB_CONFIG)
    
    # Get all rules without embeddings
    with conn.cursor() as cur:
        cur.execute("SELECT id, rule FROM rules WHERE embedding IS NULL")
        rules = cur.fetchall()
    
    print(f"Found {len(rules)} rules to process")
    
    if not rules:
        print("No rules need processing!")
        return
    
    # Process each rule
    for i, (rule_id, rule_text) in enumerate(rules, 1):
        print(f"Processing rule {i}/{len(rules)}: ID {rule_id}")
        
        # Generate embedding
        embedding = model.encode([rule_text])[0]
        
        # Store in database
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE rules SET embedding = %s WHERE id = %s",
                (embedding.tolist(), rule_id)
            )
        conn.commit()
    
    print("Done! All embeddings created and stored.")
    conn.close()

if __name__ == "__main__":
    main()
