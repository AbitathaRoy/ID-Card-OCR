# src/query.py

import sqlite3
from src.database import get_connection
from src.validate import validate_record

def get_unallocated():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM students
        WHERE allocated = 0
    """)

    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

def get_unallocated_by_category(category: str):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM students
        WHERE allocated = 0
          AND typed_categories LIKE ?
    """, (f"%{category}%",))

    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows

def get_candidates(category: str, min_confidence: float = 0.8):
    candidates = get_unallocated_by_category(category)

    qualified = []
    for row in candidates:
        scores = validate_record(row)
        if scores["overall_confidence"] >= min_confidence:
            qualified.append((row, scores))

    return qualified

def get_all_students():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM students")
    rows = [dict(row) for row in cur.fetchall()]

    conn.close()
    return rows


def get_students_by_category(category: str):
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT * FROM students
        WHERE typed_categories LIKE ?
    """, (f"%{category}%",))

    rows = [dict(row) for row in cur.fetchall()]
    conn.close()
    return rows


def allocate_student(email: str, event_name: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE students
        SET allocated = 1,
            allocated_event = ?
        WHERE email = ?
    """, (event_name, email))

    conn.commit()
    conn.close()

def unallocate_student(email: str):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE students
        SET allocated = 0,
            allocated_event = NULL
        WHERE email = ?
    """, (email,))

    conn.commit()
    conn.close()
