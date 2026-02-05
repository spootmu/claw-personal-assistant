"""
Database Module for Claw Personal Assistant

Implements SQLite-based storage for structured data, following the
three-tier memory architecture discussed in the Moltbook community.
"""

import sqlite3
import json
import os
from datetime import datetime
from typing import Any, Dict, List, Optional


class DatabaseManager:
    """Manages SQLite database for structured data storage"""
    
    def __init__(self, db_path: str = "./claw_data.db"):
        self.db_path = db_path
        self.connection = None
        self.init_database()
        
    def init_database(self):
        """Initialize the database and create required tables"""
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row  # Enable column access by name
        self.connection.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
        
        # Create tables
        self._create_interactions_table()
        self._create_learnings_table()
        self._create_community_insights_table()
        self._create_sessions_table()
        
        self.connection.commit()
        
    def _create_interactions_table(self):
        """Create table for storing interactions"""
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                user_input TEXT,
                assistant_response TEXT,
                context TEXT,
                metadata TEXT
            )
        """)
        
    def _create_learnings_table(self):
        """Create table for storing learnings"""
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS learnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                learning_content TEXT NOT NULL,
                source TEXT,
                tags TEXT,
                relevance_score REAL DEFAULT 1.0
            )
        """)
        
    def _create_community_insights_table(self):
        """Create table for storing community insights"""
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS community_insights (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                source TEXT NOT NULL,
                topic TEXT NOT NULL,
                insight TEXT NOT NULL,
                processed BOOLEAN DEFAULT FALSE
            )
        """)
        
    def _create_sessions_table(self):
        """Create table for storing session data"""
        self.connection.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_key TEXT UNIQUE NOT NULL,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT DEFAULT 'active',
                metadata TEXT
            )
        """)
        
    def store_interaction(self, user_input: str, assistant_response: str, context: dict = None, metadata: dict = None):
        """Store an interaction in the database"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO interactions (timestamp, user_input, assistant_response, context, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            user_input,
            assistant_response,
            json.dumps(context) if context else None,
            json.dumps(metadata) if metadata else None
        ))
        self.connection.commit()
        return cursor.lastrowid
        
    def store_learning(self, learning_content: str, source: str = None, tags: List[str] = None, relevance_score: float = 1.0):
        """Store a learning in the database"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO learnings (timestamp, learning_content, source, tags, relevance_score)
            VALUES (?, ?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            learning_content,
            source,
            json.dumps(tags) if tags else None,
            relevance_score
        ))
        self.connection.commit()
        return cursor.lastrowid
        
    def store_community_insight(self, source: str, topic: str, insight: str):
        """Store a community insight in the database"""
        cursor = self.connection.cursor()
        cursor.execute("""
            INSERT INTO community_insights (timestamp, source, topic, insight)
            VALUES (?, ?, ?, ?)
        """, (
            datetime.now().isoformat(),
            source,
            topic,
            insight
        ))
        self.connection.commit()
        return cursor.lastrowid
        
    def get_recent_interactions(self, limit: int = 10) -> List[Dict]:
        """Get recent interactions from the database"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM interactions 
            ORDER BY timestamp DESC 
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    def search_learnings(self, query: str, limit: int = 10) -> List[Dict]:
        """Search learnings by content"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM learnings 
            WHERE learning_content LIKE ? OR tags LIKE ?
            ORDER BY relevance_score DESC
            LIMIT ?
        """, (f"%{query}%", f"%{query}%", limit))
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    def get_unprocessed_community_insights(self) -> List[Dict]:
        """Get community insights that haven't been processed yet"""
        cursor = self.connection.cursor()
        cursor.execute("""
            SELECT * FROM community_insights 
            WHERE processed = FALSE
            ORDER BY timestamp ASC
        """)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
        
    def mark_insight_as_processed(self, insight_id: int):
        """Mark a community insight as processed"""
        cursor = self.connection.cursor()
        cursor.execute("""
            UPDATE community_insights 
            SET processed = TRUE 
            WHERE id = ?
        """, (insight_id,))
        self.connection.commit()
        
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()