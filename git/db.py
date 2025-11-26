import sqlite3

def init_db(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS repos (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE,
            owner TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_owner(db_path, repo_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('SELECT owner FROM repos WHERE name = ?', (repo_name,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None