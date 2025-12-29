import os
import sqlite3

db_path = os.path.expanduser("~/syndicate/data/syndicate.db")
conn = sqlite3.connect(db_path)
cur = conn.cursor()
cur.execute('UPDATE llm_tasks SET status = "pending" WHERE status = "in_progress"')
print(f"Reset {cur.rowcount} tasks to pending.")
conn.commit()
conn.close()
