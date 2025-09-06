import json
import psycopg2
from psycopg2.extras import RealDictCursor
import argparse
from datetime import datetime
from typing import Dict, List, Optional

## written by claude

# Database configuration - UPDATE THESE
DB_CONFIG = {
    'host': 'localhost',
    'database': 'postgres',
    'user': 'postgres', 
    'password': 'postgres',
    'port': 5432
}

class GameRulesProcessor:
    def __init__(self, db_config: Dict[str, str]):
        """
        Initialize the processor with database configuration.
        
        Args:
            db_config: Dictionary with keys: host, database, user, password, port
        """
        self.db_config = db_config
        self.connection = None
    
    def connect_to_database(self):
        """Establish connection to PostgreSQL database."""
        try:
            self.connection = psycopg2.connect(
                host=self.db_config['host'],
                database=self.db_config['database'],
                user=self.db_config['user'],
                password=self.db_config['password'],
                port=self.db_config.get('port', 5432)
            )
            print("✅ Successfully connected to PostgreSQL database")
        except psycopg2.Error as e:
            print(f"❌ Error connecting to PostgreSQL database: {e}")
            raise
    
    def close_connection(self):
        """Close database connection."""
        if self.connection:
            self.connection.close()
            print("🔒 Database connection closed")
    
    def create_or_get_game(self, game_name: str, game_version: str = "1.0") -> int:
        """
        Create a new game entry or get existing game ID.
        
        Args:
            game_name: Name of the game
            game_version: Version of the game
            
        Returns:
            game_id: ID of the game record
        """
        cursor = self.connection.cursor(cursor_factory=RealDictCursor)
        
        try:
            # Check if game already exists
            cursor.execute(
                "SELECT id FROM games WHERE name = %s AND version = %s",
                (game_name, game_version)
            )
            existing_game = cursor.fetchone()
            
            if existing_game:
                print(f"📋 Found existing game: {game_name} v{game_version} (ID: {existing_game['id']})")
                return existing_game['id']
            
            # Create new game
            cursor.execute(
                """
                INSERT INTO games (name, version, created_at, updated_at)
                VALUES (%s, %s, %s, %s)
                RETURNING id
                """,
                (game_name, game_version, datetime.now(), datetime.now())
            )
            
            game_id = cursor.fetchone()['id']
            self.connection.commit()
            print(f"✨ Created new game: {game_name} v{game_version} (ID: {game_id})")
            return game_id
            
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"❌ Error creating/getting game: {e}")
            raise
        finally:
            cursor.close()
    
    def insert_rules(self, game_id: int, rules_text: List[str]):
        """
        Insert rules into the database.
        
        Args:
            game_id: ID of the game
            rules_text: List of rule text strings
        """
        cursor = self.connection.cursor()
        
        try:
            # Insert rules in batch
            rules_data = [
                (rule_text.strip(), datetime.now(), datetime.now(), game_id)
                for rule_text in rules_text
                if rule_text.strip()  # Skip empty rules
            ]
            
            if not rules_data:
                print("⚠️ No valid rules found to insert")
                return
            
            cursor.executemany(
                """
                INSERT INTO rules (rule, created_at, updated_at, game_id)
                VALUES (%s, %s, %s, %s)
                """,
                rules_data
            )
            
            self.connection.commit()
            print(f"📝 Successfully inserted {len(rules_data)} rules for game ID {game_id}")
            
        except psycopg2.Error as e:
            self.connection.rollback()
            print(f"❌ Error inserting rules: {e}")
            raise
        finally:
            cursor.close()
    
    def load_json_file(self, file_path: str) -> Dict:
        """
        Load and parse JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            Parsed JSON data
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
                print(f"📁 Successfully loaded JSON file: {file_path}")
                return data
        except FileNotFoundError:
            print(f"❌ File not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing JSON file: {e}")
            raise
    
    def process_json_file(self, file_path: str, game_name: str, game_version: str = "1.0"):
        """
        Process JSON file and store data in PostgreSQL.
        
        Args:
            file_path: Path to the JSON file
            game_name: Name of the game
            game_version: Version of the game
        """
        try:
            # Load JSON data
            json_data = self.load_json_file(file_path)
            
            # Validate JSON structure
            if 'pages' not in json_data:
                raise ValueError("JSON must contain 'pages' key")
            
            if not isinstance(json_data['pages'], list):
                raise ValueError("'pages' must be a list")
            
            # Extract text from pages
            rules_text = []
            for i, page in enumerate(json_data['pages']):
                if isinstance(page, dict) and 'text' in page:
                    rules_text.append(page['text'])
                else:
                    print(f"⚠️ Skipping page {i}: missing 'text' field")
            
            print(f"📖 Found {len(rules_text)} pages with text content")
            
            # Connect to database
            self.connect_to_database()
            
            # Create or get game
            game_id = self.create_or_get_game(game_name, game_version)
            
            # Insert rules
            self.insert_rules(game_id, rules_text)
            
            print("🎉 Processing completed successfully!")
            
        except Exception as e:
            print(f"❌ Error processing file: {e}")
            raise
        finally:
            self.close_connection()


def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Parse JSON file and store in PostgreSQL database')
    parser.add_argument('json_file', help='Path to the JSON file')
    parser.add_argument('game_name', help='Name of the game')
    parser.add_argument('--game-version', default='1.0', help='Version of the game (default: 1.0)')
    
    args = parser.parse_args()
    
    # Process the file using the global DB_CONFIG
    processor = GameRulesProcessor(DB_CONFIG)
    processor.process_json_file(args.json_file, args.game_name, args.game_version)


if __name__ == "__main__":
    main()


# Example usage:
"""
# Command line usage:
python json_parser.py rules.json "Dungeons & Dragons"
python json_parser.py rules.json "My Game" --game-version "2.0"

# Programmatic usage:
processor = GameRulesProcessor(DB_CONFIG)
processor.process_json_file('rules.json', 'My Game', '2.0')
"""
