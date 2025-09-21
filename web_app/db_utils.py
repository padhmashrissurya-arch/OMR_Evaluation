import sqlite3

DB_PATH = "students.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS results (
            student_id TEXT PRIMARY KEY,
            student_name TEXT,
            version TEXT,
            subject_1 INTEGER,
            subject_2 INTEGER,
            subject_3 INTEGER,
            subject_4 INTEGER,
            subject_5 INTEGER,
            total INTEGER,
            review TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_result(student_id, student_name, version, results):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT OR REPLACE INTO results (student_id, student_name, version, subject_1, subject_2, subject_3, subject_4, subject_5, total, review)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, COALESCE((SELECT review FROM results WHERE student_id=?), ''))
    """, (
        student_id, student_name, version,
        results.get("subject_1", 0),
        results.get("subject_2", 0),
        results.get("subject_3", 0),
        results.get("subject_4", 0),
        results.get("subject_5", 0),
        results.get("total", 0),
        student_id
    ))
    conn.commit()
    conn.close()

def get_all_results():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT * FROM results")
    rows = c.fetchall()
    columns = [desc[0] for desc in c.description]
    conn.close()
    return [dict(zip(columns, row)) for row in rows]

def save_review(student_id, review):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("UPDATE results SET review=? WHERE student_id=?", (review, student_id))
    conn.commit()
    conn.close()

def delete_result(student_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("DELETE FROM results WHERE student_id=?", (student_id,))
    conn.commit()
    conn.close() 