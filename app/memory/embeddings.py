import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict
from .database import MemoryDatabase

class MemoryRetriever:
    def __init__(self, db_path: str = "data/memory.db"):
        """Initialize semantic search with a lightweight embedding model"""
        # Use a small, fast model that runs on CPU
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.db = MemoryDatabase(db_path)
    
    def embed_text(self, text: str) -> np.ndarray:
        """Generate embedding for text"""
        return self.model.encode(text, convert_to_numpy=True)
    
    def store_with_embedding(
        self, 
        session_id: str, 
        role: str, 
        content: str, 
        metadata: Dict = None
    ) -> int:
        """Store message and its embedding"""
        # Store the message
        message_id = self.db.store_message(session_id, role, content, metadata)
        
        # Generate and store embedding
        embedding = self.embed_text(content)
        
        # Store embedding in database
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO embeddings (conversation_id, embedding) VALUES (?, ?)",
            (message_id, embedding.astype(np.float32).tobytes())
        )
        
        conn.commit()
        conn.close()
        
        return message_id
    
    def search_similar(
        self, 
        query: str, 
        session_id: str = None, 
        top_k: int = 5
    ) -> List[Dict]:
        """Search for semantically similar messages"""
        # Generate query embedding
        query_embedding = self.embed_text(query)
        
        # Get all messages with embeddings
        import sqlite3
        conn = sqlite3.connect(self.db.db_path)
        cursor = conn.cursor()
        
        if session_id:
            cursor.execute("""
                SELECT c.id, c.role, c.content, c.timestamp, e.embedding
                FROM conversations c
                JOIN embeddings e ON c.id = e.conversation_id
                WHERE c.session_id = ?
            """, (session_id,))
        else:
            cursor.execute("""
                SELECT c.id, c.role, c.content, c.timestamp, e.embedding
                FROM conversations c
                JOIN embeddings e ON c.id = e.conversation_id
            """)
        
        results = []
        for row in cursor.fetchall():
            msg_id, role, content, timestamp, embedding_blob = row
            embedding = np.frombuffer(embedding_blob, dtype=np.float32)
            
            # Cosine similarity
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            
            results.append({
                'id': msg_id,
                'role': role,
                'content': content,
                'timestamp': timestamp,
                'similarity': float(similarity)
            })
        
        conn.close()
        
        # Sort by similarity and return top k
        results.sort(key=lambda x: x['similarity'], reverse=True)
        return results[:top_k]
    
    def get_context_for_query(
        self, 
        query: str, 
        session_id: str, 
        max_tokens: int = 2000
    ) -> str:
        """Get relevant context for a query"""
        # Get recent messages (always include)
        recent = self.db.get_recent_messages(session_id, limit=5)
        
        # Get semantically similar messages
        similar = self.search_similar(query, session_id, top_k=3)
        
        # Build context string
        context_parts = []
        
        # Add recent context
        if recent:
            context_parts.append("## Recent Conversation:")
            for msg in recent:
                context_parts.append(f"{msg['role']}: {msg['content']}")
        
        # Add relevant past context
        if similar:
            context_parts.append("\n## Relevant Past Context:")
            for msg in similar:
                if msg['id'] not in [m['id'] for m in recent]:  # Avoid duplicates
                    context_parts.append(
                        f"{msg['role']}: {msg['content']} (similarity: {msg['similarity']:.2f})"
                    )
        
        return "\n".join(context_parts)
