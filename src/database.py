import sqlite3
from pathlib import Path

DB_PATH = Path("data/finance.db")

def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_table():

    conn = get_connection()
    cursor=conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
                   id INTEGER PRIMARY KEY AUTOINCREMENT,
                   date TEXT NOT NULL,
                   type TEXT NOT NULL,
                   category TEXT NOT NULL,
                   amount REAL NOT NULL,
                   note TEXT
                   )
    """)

    conn.commit()
    conn.close()

def add_transaction(date, type_, category, amount, note=""):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    INSERT INTO transactions (date, type, category, amount, note)
    VALUES (?, ?, ?, ?, ?)
    """, (date, type_, category, amount, note))

    conn.commit()
    conn.close()

def get_all_transactions():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT id, date, type, category, amount, note
    FROM transactions
    ORDER BY date DESC
    """)

    rows = cursor.fetchall()
    conn.close()
    return rows

def delete_transaction(transaction_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""DELETE FROM transactions WHERE id = ?""", (transaction_id,))

    conn.commit()
    conn.close()

    
def remove_all_transactions(reset_id: bool = True):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM transactions")

    if reset_id:
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='transactions'")

    conn.commit()
    conn.close()

def update_transaction(transaction_id, date, type_, category, amount, note):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    UPDATE transactions
    SET date = ?, type = ?, category = ?, amount = ?, note = ?
    WHERE id = ?

    """, (date, type_, category, amount, note, transaction_id))

    conn.commit()
    conn.close()