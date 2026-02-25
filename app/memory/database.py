import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

class MemoryDatabase:
    def __init__(self, db_path: str = "data/memory.db"):
        """Initialize the memory database"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.init_db()
    
    def init_db(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                metadata TEXT
            )
        """)
        
        # Embeddings table for semantic search
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                embedding BLOB NOT NULL,
                FOREIGN KEY (conversation_id) REFERENCES conversations(id)
            )
        """)
        
        conn.commit()
        conn.close()
    
    def store_message(
        self, 
        session_id: str, 
        role: str, 
        content: str, 
        metadata: Optional[Dict] = None
    ) -> int:
        """Store a message in the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            INSERT INTO conversations (session_id, role, content, metadata)
            VALUES (?, ?, ?, ?)
            """,
            (session_id, role, content, json.dumps(metadata) if metadata else None)
        )
        
        message_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return message_id
    
    def get_recent_messages(
        self, 
        session_id: str, 
        limit: int = 10
    ) -> List[Dict]:
        """Get recent messages from a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            """
            SELECT id, timestamp, role, content, metadata
            FROM conversations
            WHERE session_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
            """,
            (session_id, limit)
        )
        
        messages = []
        for row in cursor.fetchall():
            messages.append({
                'id': row[0],
                'timestamp': row[1],
                'role': row[2],
                'content': row[3],
                'metadata': json.loads(row[4]) if row[4] else None
            })
        
        conn.close()
        return list(reversed(messages))  # Return chronological order
    
    def get_all_sessions(self) -> List[str]:
        """Get all unique session IDs"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT session_id FROM conversations ORDER BY timestamp DESC")
        sessions = [row[0] for row in cursor.fetchall()]
        
        conn.close()
        return sessions
    
    def clear_session(self, session_id: str):
        """Clear all messages from a session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
        
        conn.commit()
        conn.close()
