import os
import sqlite3
from typing import List, Tuple

RAG_DB_PATH = "device_knowledge_base.db"

def initialize_knowledge_base():
    """Guarantees the local RAG text schema is active on the host machine."""
    conn = sqlite3.connect(RAG_DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS device_manual_chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            machine_model TEXT NOT NULL,
            section_title TEXT,
            content TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()

def save_manual_chunk(machine_model: str, section_title: str, text_content: str):
    """Inserts a processed section of a technical service manual into the DB."""
    initialize_knowledge_base()
    conn = sqlite3.connect(RAG_DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO device_manual_chunks (machine_model, section_title, content)
        VALUES (?, ?, ?);
    """, (machine_model, section_title, text_content))
    conn.commit()
    conn.close()

def query_device_manual(machine_model: str, query_keyword: str) -> List[Tuple[str, str]]:
    """Scans the manual database text fields to pull out exact solutions."""
    initialize_knowledge_base()
    conn = sqlite3.connect(RAG_DB_PATH)
    cur = conn.cursor()
    
    search_query = """
    SELECT section_title, content FROM device_manual_chunks 
    WHERE machine_model = ? AND (content LIKE ? OR section_title LIKE ?);
    """
    like_pattern = f"%{query_keyword}%"
    cur.execute(search_query, (machine_model, like_pattern, like_pattern))
    rows = cur.fetchall()
    
    cur.close()
    conn.close()
    return rows
