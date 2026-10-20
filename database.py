"""
database.py - Database operations for Student Record Management System.

This module handles all SQLite database operations including table creation,
inserting, reading, updating, and deleting student records using parameterized
queries to prevent SQL injection.
"""

import sqlite3
import os

# Default database filename in current directory
DEFAULT_DB_NAME = "students.db"


def get_db_path(db_name=None):
    """Resolve database path relative to current project directory."""
    if db_name:
        return db_name
    # Use environment variable if set (useful for testing), else default
    return os.environ.get("STUDENT_DB_PATH", DEFAULT_DB_NAME)


def get_db_connection(db_name=None):
    """
    Establish and return a connection to the SQLite database.
    row_factory is set to sqlite3.Row so columns can be accessed by name.
    """
    db_path = get_db_path(db_name)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_name=None):
    """
    Initialize the database by creating the 'students' table if it doesn't exist.
    """
    db_path = get_db_path(db_name)
    conn = get_db_connection(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            course TEXT NOT NULL,
            year_of_study TEXT NOT NULL,
            admission_date TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def get_all_students(search=None, course=None, db_name=None):
    """
    Retrieve all students with optional search query and course filter.
    Returns a list of dictionaries.
    """
    conn = get_db_connection(db_name)
    cursor = conn.cursor()

    query = "SELECT * FROM students WHERE 1=1"
    params = []

    if search:
        search_pattern = f"%{search.strip()}%"
        query += " AND (full_name LIKE ? OR CAST(id AS TEXT) LIKE ?)"
        params.extend([search_pattern, search_pattern])

    if course and course.strip():
        query += " AND course = ?"
        params.append(course.strip())

    query += " ORDER BY id ASC"

    cursor.execute(query, params)
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_student_by_id(student_id, db_name=None):
    """
    Retrieve a single student record by primary key ID.
    Returns a dictionary or None if not found.
    """
    conn = get_db_connection(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def get_student_by_email(email, db_name=None):
    """
    Retrieve a student record by email address.
    Used to check for duplicate emails.
    """
    conn = get_db_connection(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM students WHERE LOWER(email) = LOWER(?)", (email.strip(),))
    row = cursor.fetchone()
    conn.close()

    return dict(row) if row else None


def add_student(full_name, email, phone, course, year_of_study, admission_date, db_name=None):
    """
    Insert a new student record into the database.
    Returns the newly generated student ID.
    """
    conn = get_db_connection(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO students (full_name, email, phone, course, year_of_study, admission_date)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        full_name.strip(),
        email.strip(),
        phone.strip() if phone else None,
        course.strip(),
        year_of_study.strip(),
        admission_date.strip()
    ))

    new_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return new_id


def update_student(student_id, full_name, email, phone, course, year_of_study, admission_date, db_name=None):
    """
    Update an existing student record by ID.
    Returns True if a row was updated, False if student was not found.
    """
    conn = get_db_connection(db_name)
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE students
        SET full_name = ?, email = ?, phone = ?, course = ?, year_of_study = ?, admission_date = ?
        WHERE id = ?
    """, (
        full_name.strip(),
        email.strip(),
        phone.strip() if phone else None,
        course.strip(),
        year_of_study.strip(),
        admission_date.strip(),
        student_id
    ))

    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0


def delete_student(student_id, db_name=None):
    """
    Delete a student record by ID.
    Returns True if a row was deleted, False if student was not found.
    """
    conn = get_db_connection(db_name)
    cursor = conn.cursor()

    cursor.execute("DELETE FROM students WHERE id = ?", (student_id,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    return rows_affected > 0


def get_all_courses(db_name=None):
    """
    Retrieve a sorted list of unique courses currently in the database.
    """
    conn = get_db_connection(db_name)
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT course FROM students WHERE course IS NOT NULL AND course != '' ORDER BY course ASC")
    rows = cursor.fetchall()
    conn.close()

    return [row["course"] for row in rows]


def seed_sample_data(db_name=None):
    """
    Seed initial academic sample records if the database is currently empty.
    """
    conn = get_db_connection(db_name)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) AS count FROM students")
    count = cursor.fetchone()["count"]

    if count == 0:
        sample_students = [
            ("Eleanor Vance", "eleanor.vance@college.edu", "555-0142", "Computer Science", "Year 2", "2024-09-01"),
            ("Marcus Thorne", "marcus.thorne@college.edu", "555-0188", "Mechanical Engineering", "Year 3", "2023-09-01"),
            ("Sophia Chen", "sophia.chen@college.edu", "555-0193", "Information Technology", "Year 1", "2025-01-15"),
            ("Liam O'Connor", "liam.oconnor@college.edu", "555-0177", "Business Administration", "Year 4", "2022-09-01")
        ]
        cursor.executemany("""
            INSERT INTO students (full_name, email, phone, course, year_of_study, admission_date)
            VALUES (?, ?, ?, ?, ?, ?)
        """, sample_students)
        conn.commit()
        print(f"Database seeded with {len(sample_students)} sample student records.")
    else:
        print(f"Database already contains {count} record(s). Skipping seeding.")

    conn.close()


if __name__ == "__main__":
    print(f"Initializing database: {DEFAULT_DB_NAME}")
    init_db()
    seed_sample_data()
    print("Database initialization complete.")
