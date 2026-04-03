import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "nippou.db")

def get_connection():
    # DBに接続
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    # テーブルがなければ作成
    conn.execute("""
          CREATE TABLE IF NOT EXISTS daily_reports (
              date       TEXT PRIMARY KEY,
              timeblock  TEXT NOT NULL,
              theme      TEXT NOT NULL,
              details    TEXT NOT NULL,
              tomorrow   TEXT NOT NULL,
              note       TEXT,
              created_at TEXT NOT NULL,
              updated_at TEXT NOT NULL
          )
      """)
    conn.commit()
    conn.close()
