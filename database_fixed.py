import sqlite3
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
import logging

class DatabaseManager:
    """
    Manages the SQLite database for storing interactions, learnings, and community insights.
    """
    
    def __init__(self, db_path: str, db_type: str = "main"):
        self.db_path = db_path
        self.db_type = db_type
        self.logger = logging.getLogger(f"{__name__}.{db_type}")
        self.init_database()
        
    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_input TEXT,
                assistant_response TEXT,
                context TEXT  -- JSON string for additional context
            )
        ''')
        
        # Create learnings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS learnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                learning_content TEXT NOT NULL,
                source TEXT,
                tags TEXT  -- JSON string for tags array
            )
        ''')
        
        # Create community insights table with proper constraints
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS community_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                topic TEXT NOT NULL,
                insight TEXT NOT NULL,
                UNIQUE(source, topic, insight)  -- Prevent exact duplicates
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_learnings_timestamp ON learnings(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_learnings_source ON learnings(source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_community_timestamp ON community_insights(timestamp)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_community_source ON community_insights(source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_community_topic ON community_insights(topic)')
        
        conn.commit()
        conn.close()
        
        self.logger.info(f"Database initialized at {self.db_path}")
        
    def store_interaction(self, user_input: str, assistant_response: str, context: Dict[str, Any] = None):
        """Store an interaction in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO interactions (timestamp, user_input, assistant_response, context)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                user_input,
                assistant_response,
                json.dumps(context) if context else None
            ))
            conn.commit()
            self.logger.debug(f"Stored interaction: {user_input[:50]}...")
        except Exception as e:
            self.logger.error(f"Failed to store interaction: {e}")
        finally:
            conn.close()
    
    def store_learning(self, learning_content: str, source: str = None, tags: List[str] = None):
        """Store a learning in the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO learnings (timestamp, learning_content, source, tags)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                learning_content,
                source,
                json.dumps(tags) if tags else None
            ))
            conn.commit()
            self.logger.debug(f"Stored learning: {learning_content[:50]}...")
        except Exception as e:
            self.logger.error(f"Failed to store learning: {e}")
        finally:
            conn.close()
    
    def store_community_insight(self, source: str, topic: str, insight: str):
        """Store a community insight in the database, avoiding duplicates."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Use INSERT OR IGNORE to handle the UNIQUE constraint gracefully
            cursor.execute('''
                INSERT OR IGNORE INTO community_insights (timestamp, source, topic, insight)
                VALUES (?, ?, ?, ?)
            ''', (
                datetime.now().isoformat(),
                source,
                topic,
                insight
            ))
            conn.commit()
            
            # Check if the record was actually inserted
            if cursor.rowcount > 0:
                self.logger.debug(f"Stored community insight: {source} - {topic}")
            else:
                self.logger.debug(f"Ignored duplicate community insight: {source} - {topic}")
        except Exception as e:
            self.logger.error(f"Failed to store community insight: {e}")
        finally:
            conn.close()
    
    def get_recent_interactions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent interactions from the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                SELECT timestamp, user_input, assistant_response, context
                FROM interactions
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (limit,))
            
            rows = cursor.fetchall()
            interactions = []
            for row in rows:
                interaction = {
                    'timestamp': row[0],
                    'user_input': row[1],
                    'assistant_response': row[2],
                    'context': json.loads(row[3]) if row[3] else {}
                }
                interactions.append(interaction)
                
            return interactions
        except Exception as e:
            self.logger.error(f"Failed to retrieve interactions: {e}")
            return []
        finally:
            conn.close()
    
    def search_learnings(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for learnings that match the query."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Search in learning_content and source fields
            cursor.execute('''
                SELECT timestamp, learning_content, source, tags
                FROM learnings
                WHERE learning_content LIKE ? OR source LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            rows = cursor.fetchall()
            learnings = []
            for row in rows:
                learning = {
                    'timestamp': row[0],
                    'learning_content': row[1],
                    'source': row[2],
                    'tags': json.loads(row[3]) if row[3] else [],
                    'relevance_score': 1.0  # Basic relevance for now
                }
                learnings.append(learning)
                
            return learnings
        except Exception as e:
            self.logger.error(f"Failed to search learnings: {e}")
            return []
        finally:
            conn.close()
    
    def search_community_insights(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for community insights that match the query."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Search in topic and insight fields
            cursor.execute('''
                SELECT timestamp, source, topic, insight
                FROM community_insights
                WHERE topic LIKE ? OR insight LIKE ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', limit))
            
            rows = cursor.fetchall()
            insights = []
            for row in rows:
                insight = {
                    'timestamp': row[0],
                    'source': row[1],
                    'topic': row[2],
                    'content': row[3]
                }
                insights.append(insight)
                
            return insights
        except Exception as e:
            self.logger.error(f"Failed to search community insights: {e}")
            return []
        finally:
            conn.close()
    
    def get_all_sources(self) -> List[str]:
        """Get all unique sources from community insights."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('SELECT DISTINCT source FROM community_insights')
            rows = cursor.fetchall()
            return [row[0] for row in rows]
        except Exception as e:
            self.logger.error(f"Failed to get sources: {e}")
            return []
        finally:
            conn.close()
    
    def export_data(self, export_path: str):
        """Export all data to a JSON file."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Export interactions
            cursor.execute('SELECT * FROM interactions')
            interactions = cursor.fetchall()
            
            # Export learnings
            cursor.execute('SELECT * FROM learnings')
            learnings = cursor.fetchall()
            
            # Export community insights
            cursor.execute('SELECT * FROM community_insights')
            insights = cursor.fetchall()
            
            export_data = {
                'interactions': interactions,
                'learnings': learnings,
                'community_insights': insights,
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(export_data, f, indent=2, default=str)
                
            self.logger.info(f"Data exported to {export_path}")
        except Exception as e:
            self.logger.error(f"Failed to export data: {e}")
        finally:
            conn.close()