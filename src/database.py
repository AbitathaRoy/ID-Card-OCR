# src/database.py

import sqlite3
from pathlib import Path

DB_PATH = Path("data/volunteer.db")

def get_connection():
    """Create and return a SQLite connection."""
    return sqlite3.connect(DB_PATH)

def init_db():
    """Initialize the database and create tables if they don't exist."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS students (
        email TEXT PRIMARY KEY,

        -- Typed (form truth)
        typed_name TEXT NOT NULL,
        typed_course_code TEXT NOT NULL,
        typed_year_of_study INTEGER NOT NULL,
        typed_phone TEXT NOT NULL,
        typed_categories TEXT NOT NULL,

        -- OCR extracted
        ocr_name TEXT,
        ocr_admission_no TEXT UNIQUE,
        ocr_phone TEXT,

        -- Derived
        admission_year INTEGER,
        batch_end_year INTEGER,
        computed_year_of_study INTEGER,

        -- Allocation
        allocated INTEGER DEFAULT 0,
        allocated_event TEXT,

        -- Metadata
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.commit()
    conn.close()


def insert_student(record: dict):
    pass

def insert_or_update_student(form_data: dict,
                             ocr_data: dict,
                             derived_data: dict):
    """
    Insert a new student or update existing one based on email.
    """
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO students (
        email,
        typed_name,
        typed_course_code,
        typed_year_of_study,
        typed_phone,
        typed_categories,

        ocr_name,
        ocr_admission_no,
        ocr_phone,

        admission_year,
        batch_end_year,
        computed_year_of_study
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(email) DO UPDATE SET
        typed_name = excluded.typed_name,
        typed_course_code = excluded.typed_course_code,
        typed_year_of_study = excluded.typed_year_of_study,
        typed_phone = excluded.typed_phone,
        typed_categories = excluded.typed_categories,

        ocr_name = excluded.ocr_name,
        ocr_admission_no = excluded.ocr_admission_no,
        ocr_phone = excluded.ocr_phone,

        admission_year = excluded.admission_year,
        batch_end_year = excluded.batch_end_year,
        computed_year_of_study = excluded.computed_year_of_study;
    """, (
        form_data["email"],
        form_data["name"],
        form_data["course_code"],
        form_data["year_of_study"],
        form_data["phone"],
        form_data["categories_csv"],

        ocr_data.get("name"),
        ocr_data.get("admission_no"),
        ocr_data.get("phone"),

        derived_data.get("admission_year"),
        derived_data.get("batch_end_year"),
        derived_data.get("computed_year")
    ))

    conn.commit()
    conn.close()



def update_allocation(admission_no: str, event: str):
    pass

def fetch_all_students():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT * FROM students;")
    rows = cur.fetchall()

    conn.close()
    return rows

def fetch_all_students_as_dict():
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT * FROM students;")
    rows = [dict(row) for row in cur.fetchall()]

    conn.close()
    return rows
