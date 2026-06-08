import sqlite3

import pytest

from book_tracker import create_app


@pytest.fixture()
def app(tmp_path):
    db_path = tmp_path / "test.sqlite"
    app = create_app({"TESTING": True, "DATABASE": str(db_path)})
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def get_rows(app):
    conn = sqlite3.connect(app.config["DATABASE"])
    conn.row_factory = sqlite3.Row
    return conn


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 200


def test_add_book(client, app):
    response = client.post(
        "/books/new",
        data={
            "title": "Clean Code",
            "author": "Robert C. Martin",
            "genre": "Programming",
            "pages": "464",
            "status": "reading",
            "rating": "5",
            "notes": "For practice",
        },
        follow_redirects=False,
    )
    assert response.status_code == 302
    with get_rows(app) as conn:
        row = conn.execute("SELECT title, author FROM books").fetchone()
    assert row["title"] == "Clean Code"
    assert row["author"] == "Robert C. Martin"


def test_search_and_filter(client, app):
    with get_rows(app) as conn:
        conn.execute(
            "INSERT INTO books (title, author, genre, pages, status, rating, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("Dune", "Frank Herbert", "Sci-Fi", 500, "done", 5, ""),
        )
        conn.execute(
            "INSERT INTO books (title, author, genre, pages, status, rating, notes) VALUES (?, ?, ?, ?, ?, ?, ?)",
            ("Book of Tests", "Alice Example", "Education", 120, "want", None, ""),
        )
        conn.commit()

    response = client.get("/?q=dune&status=done")
    assert response.status_code == 200
    body = response.get_data(as_text=True)
    assert "Dune" in body
    assert "Book of Tests" not in body


def test_404_for_missing_book(client):
    response = client.get("/books/999")
    assert response.status_code == 404


def test_validation_rejects_empty_title(client):
    response = client.post(
        "/books/new",
        data={
            "title": "",
            "author": "Someone",
            "genre": "Memoir",
            "pages": "100",
            "status": "want",
            "rating": "",
            "notes": "",
        },
    )
    assert response.status_code == 400
    assert "Поле «Название» обязательно." in response.get_data(as_text=True)

