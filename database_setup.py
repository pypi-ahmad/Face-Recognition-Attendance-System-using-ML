import sqlite3
import chromadb
import os
from datetime import datetime
import uuid

DB_NAME = "attendance.db"
CHROMA_PATH = "chroma_db"

def init_db():
    # Setup SQLite
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Table Users
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        roll_no TEXT,
        academic_year TEXT,
        semester TEXT,
        section TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Table AttendanceLogs
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS AttendanceLogs (
        log_id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        timestamp TIMESTAMP,
        status TEXT,
        confidence_score REAL,
        FOREIGN KEY(user_id) REFERENCES Users(user_id)
    )
    ''')
    
    conn.commit()
    conn.close()
    print(f"SQLite database '{DB_NAME}' initialized.")

    # Setup ChromaDB
    # Note: If this fails with "module not found", ensure pip install chromadb is done
    try:
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        client.get_or_create_collection(name="face_embeddings", metadata={"hnsw:space": "cosine"})
        print("ChromaDB collection 'face_embeddings' is ready.")
    except Exception as e:
        print(f"ChromaDB Setup Warning: {e}")

def get_sqlite_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def get_chroma_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(name="face_embeddings")

if __name__ == "__main__":
    init_db()