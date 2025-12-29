import os
import sqlite3

db_path = os.path.expanduser("~/syndicate/data/syndicate.db")
if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row
cur = conn.cursor()
cur.execute("SELECT id, document_path, status, provider_hint, error FROM llm_tasks ORDER BY id DESC LIMIT 5")
rows = cur.fetchall()
print("Recent tasks:")
for r in rows:
    print(dict(r))
conn.close()
