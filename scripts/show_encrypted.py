# show_encrypted.py - shows what is really stored in the database (for the privacy check / demo).
# usage (project root):  python -m scripts.show_encrypted
# Expected: profile / question / answer columns look like gAAAAA... (ciphertext), not readable text.
import sqlite3

from backend.app.config import DB_PATH

conn = sqlite3.connect(DB_PATH)
for label, sql in [("profile.data_enc", "SELECT data_enc FROM profile"),
                   ("history.question_enc", "SELECT question_enc FROM history LIMIT 2"),
                   ("history.answer_enc", "SELECT answer_enc FROM history LIMIT 2")]:
    rows = conn.execute(sql).fetchall()
    print(f"{label}:")
    for (value,) in rows:
        print("  ", value[:70] + ("..." if len(value) > 70 else ""))
    if not rows:
        print("   (empty)")
print("\nNot encrypted (by design): timestamps, outcome label, source list.")
