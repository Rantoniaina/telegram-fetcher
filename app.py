import os
import sqlite3
from time import sleep

def init_db():
    db_path = os.environ.get('SQLITE_DATABASE', '/app/data/database.sqlite')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create a test table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS test (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()
    print(f"Database initialized at {db_path}")

if __name__ == "__main__":
    print("Starting the application...")
    init_db()
    
    # Keep the container running
    while True:
        print("Application is running...")
        sleep(60) 