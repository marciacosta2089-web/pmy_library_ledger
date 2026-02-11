import sqlite3
from datetime import datetime
from typing import Optional
from contextlib import contextmanager

DATABASE_FILE = "library.db"

STATUSES = ["OWNED", "WISHLIST", "SUGGESTED", "BORROWED", "LENT"]


@contextmanager
def get_connection():
    """Context manager for database connections."""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()


def init_db():
    """Initialize the database and create tables if they don't exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                author TEXT,
                status TEXT NOT NULL,
                person TEXT,
                date_added TEXT NOT NULL,
                notes TEXT,
                date_updated TEXT NOT NULL
            )
        """)
        conn.commit()


def add_book(
    title: str,
    author: Optional[str],
    status: str,
    person: Optional[str],
    notes: Optional[str]
) -> int:
    """Add a new book to the database. Returns the new book's ID."""
    now = datetime.now().isoformat()
    with get_connection() as conn:
        cursor = conn.execute(
            """
            INSERT INTO books (title, author, status, person, date_added, notes, date_updated)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (title, author or "", status, person or "", now, notes or "", now)
        )
        conn.commit()
        return cursor.lastrowid


def get_all_books() -> list[dict]:
    """Retrieve all books from the database."""
    with get_connection() as conn:
        cursor = conn.execute("SELECT * FROM books ORDER BY date_added DESC")
        return [dict(row) for row in cursor.fetchall()]


def get_books_filtered(
    search_term: str = "",
    status_filter: str = "All",
    sort_by: str = "date_added DESC"
) -> list[dict]:
    """Retrieve books with optional search, status filter, and sorting."""
    query = "SELECT * FROM books WHERE 1=1"
    params = []

    if search_term:
        query += """ AND (
            title LIKE ? OR 
            author LIKE ? OR 
            person LIKE ? OR 
            notes LIKE ?
        )"""
        search_pattern = f"%{search_term}%"
        params.extend([search_pattern] * 4)

    if status_filter != "All":
        query += " AND status = ?"
        params.append(status_filter)

    query += f" ORDER BY {sort_by}"

    with get_connection() as conn:
        cursor = conn.execute(query, params)
        return [dict(row) for row in cursor.fetchall()]


def update_book_status(book_id: int, new_status: str, person: Optional[str] = None):
    """Update a book's status and optionally the person field."""
    now = datetime.now().isoformat()
    with get_connection() as conn:
        if person is not None:
            conn.execute(
                "UPDATE books SET status = ?, person = ?, date_updated = ? WHERE id = ?",
                (new_status, person, now, book_id)
            )
        else:
            conn.execute(
                "UPDATE books SET status = ?, date_updated = ? WHERE id = ?",
                (new_status, now, book_id)
            )
        conn.commit()


def update_book(
    book_id: int,
    title: str,
    author: Optional[str],
    status: str,
    person: Optional[str],
    notes: Optional[str]
):
    """Update all editable fields of a book."""
    now = datetime.now().isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            UPDATE books 
            SET title = ?, author = ?, status = ?, person = ?, notes = ?, date_updated = ?
            WHERE id = ?
            """,
            (title, author or "", status, person or "", notes or "", now, book_id)
        )
        conn.commit()


def delete_book(book_id: int):
    """Delete a book from the database."""
    with get_connection() as conn:
        conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()


def get_status_counts() -> dict[str, int]:
    """Get count of books for each status."""
    counts = {status: 0 for status in STATUSES}
    with get_connection() as conn:
        cursor = conn.execute(
            "SELECT status, COUNT(*) as count FROM books GROUP BY status"
        )
        for row in cursor.fetchall():
            if row["status"] in counts:
                counts[row["status"]] = row["count"]
    return counts
