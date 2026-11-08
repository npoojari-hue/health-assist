# database.py - SQLite storage. Personal fields are encrypted before they are saved.
import json
import sqlite3
from datetime import datetime, timezone

from .config import DB_PATH, CONSENT_VERSION
from .crypto import encrypt_text, decrypt_text


def get_conn():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS consent (
            id INTEGER PRIMARY KEY, version TEXT, accepted_at TEXT);
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY CHECK (id = 1), data_enc TEXT, updated_at TEXT);
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT, created_at TEXT,
            question_enc TEXT, answer_enc TEXT, sources_json TEXT, outcome TEXT);
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT, history_id INTEGER, rating INTEGER, created_at TEXT);
    """)
    conn.commit()
    conn.close()


# ---------- consent ----------
def save_consent():
    conn = get_conn()
    conn.execute("INSERT INTO consent (version, accepted_at) VALUES (?, ?)", (CONSENT_VERSION, now()))
    conn.commit()
    conn.close()


def has_consent() -> bool:
    conn = get_conn()
    row = conn.execute("SELECT COUNT(*) AS n FROM consent").fetchone()
    conn.close()
    return row["n"] > 0


# ---------- profile ----------
def save_profile(data: dict):
    conn = get_conn()
    conn.execute(
        "INSERT OR REPLACE INTO profile (id, data_enc, updated_at) VALUES (1, ?, ?)",
        (encrypt_text(json.dumps(data)), now()),
    )
    conn.commit()
    conn.close()


def load_profile():
    conn = get_conn()
    row = conn.execute("SELECT data_enc FROM profile WHERE id = 1").fetchone()
    conn.close()
    return json.loads(decrypt_text(row["data_enc"])) if row else None


# ---------- history and feedback ----------
def add_history(question: str, answer: str, sources: list, outcome: str) -> int:
    conn = get_conn()
    cur = conn.execute(
        "INSERT INTO history (created_at, question_enc, answer_enc, sources_json, outcome) VALUES (?,?,?,?,?)",
        (now(), encrypt_text(question), encrypt_text(answer), json.dumps(sources), outcome),
    )
    conn.commit()
    new_id = cur.lastrowid
    conn.close()
    return new_id


def list_history():
    conn = get_conn()
    rows = conn.execute("SELECT * FROM history ORDER BY id DESC LIMIT 50").fetchall()
    conn.close()
    return [{
        "id": r["id"], "created_at": r["created_at"],
        "question": decrypt_text(r["question_enc"]), "answer": decrypt_text(r["answer_enc"]),
        "sources": json.loads(r["sources_json"]), "outcome": r["outcome"],
    } for r in rows]


def add_feedback(history_id: int, rating: int):
    conn = get_conn()
    conn.execute("INSERT INTO feedback (history_id, rating, created_at) VALUES (?,?,?)",
                 (history_id, rating, now()))
    conn.commit()
    conn.close()


# ---------- delete everything (delete-my-data button) ----------
def delete_all_data():
    conn = get_conn()
    for table in ["feedback", "history", "profile", "consent"]:
        conn.execute(f"DELETE FROM {table}")
    conn.commit()
    conn.close()
