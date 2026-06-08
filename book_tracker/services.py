from dataclasses import dataclass

from .db import get_db

STATUS_OPTIONS = {
    "want": "Хочу прочитать",
    "reading": "Читаю",
    "done": "Прочитано",
}


@dataclass
class BookFormData:
    title: str
    author: str
    genre: str
    pages: int
    status: str
    rating: int | None
    notes: str


def validate_book_form(form):
    errors = []
    title = form.get("title", "").strip()
    author = form.get("author", "").strip()
    genre = form.get("genre", "").strip()
    pages_raw = form.get("pages", "").strip()
    status = form.get("status", "want").strip()
    rating_raw = form.get("rating", "").strip()
    notes = form.get("notes", "").strip()

    if not title:
        errors.append("Поле «Название» обязательно.")
    if not author:
        errors.append("Поле «Автор» обязательно.")
    if not genre:
        errors.append("Поле «Жанр» обязательно.")
    try:
        pages = int(pages_raw)
        if pages <= 0:
            errors.append("Количество страниц должно быть больше 0.")
    except ValueError:
        errors.append("Количество страниц должно быть числом.")
        pages = 0
    if status not in STATUS_OPTIONS:
        errors.append("Недопустимый статус.")
    rating = None
    if rating_raw:
        try:
            rating = int(rating_raw)
            if rating < 1 or rating > 5:
                errors.append("Оценка должна быть от 1 до 5.")
        except ValueError:
            errors.append("Оценка должна быть числом.")
    return BookFormData(title, author, genre, pages, status, rating, notes), errors


def list_books(query="", status=""):
    sql = "SELECT * FROM books WHERE 1=1"
    params = []
    if query:
        sql += " AND (LOWER(title) LIKE ? OR LOWER(author) LIKE ? OR LOWER(genre) LIKE ?)"
        like = f"%{query.lower()}%"
        params.extend([like, like, like])
    if status in STATUS_OPTIONS:
        sql += " AND status = ?"
        params.append(status)
    sql += " ORDER BY id DESC"
    return get_db().execute(sql, params).fetchall()


def get_book(book_id):
    return get_db().execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()


def add_book(data: BookFormData):
    db = get_db()
    cursor = db.execute(
        """
        INSERT INTO books (title, author, genre, pages, status, rating, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (data.title, data.author, data.genre, data.pages, data.status, data.rating, data.notes),
    )
    db.commit()
    return cursor.lastrowid


def update_book(book_id, data: BookFormData):
    db = get_db()
    db.execute(
        """
        UPDATE books
        SET title = ?, author = ?, genre = ?, pages = ?, status = ?, rating = ?, notes = ?
        WHERE id = ?
        """,
        (data.title, data.author, data.genre, data.pages, data.status, data.rating, data.notes, book_id),
    )
    db.commit()


def delete_book(book_id):
    db = get_db()
    db.execute("DELETE FROM books WHERE id = ?", (book_id,))
    db.commit()

