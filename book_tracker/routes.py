from flask import Blueprint, abort, flash, redirect, render_template, request, url_for

from .services import (
    STATUS_OPTIONS,
    add_book,
    delete_book,
    get_book,
    list_books,
    update_book,
    validate_book_form,
)

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    query = request.args.get("q", "").strip()
    status = request.args.get("status", "").strip()
    books = list_books(query=query, status=status)
    return render_template(
        "index.html",
        books=books,
        query=query,
        status=status,
        status_options=STATUS_OPTIONS,
    )


@bp.route("/books/new", methods=["GET", "POST"])
def create_book():
    if request.method == "POST":
        data, errors = validate_book_form(request.form)
        if errors:
            return render_template(
                "book_form.html",
                form=request.form,
                errors=errors,
                status_options=STATUS_OPTIONS,
                page_title="Добавить книгу",
            ), 400
        book_id = add_book(data)
        flash("Книга добавлена.")
        return redirect(url_for("main.book_detail", book_id=book_id))
    return render_template(
        "book_form.html",
        form={},
        errors=[],
        status_options=STATUS_OPTIONS,
        page_title="Добавить книгу",
    )


@bp.route("/books/<int:book_id>")
def book_detail(book_id):
    book = get_book(book_id)
    if book is None:
        abort(404)
    return render_template("book_detail.html", book=book, status_options=STATUS_OPTIONS)


@bp.route("/books/<int:book_id>/edit", methods=["GET", "POST"])
def edit_book(book_id):
    book = get_book(book_id)
    if book is None:
        abort(404)
    if request.method == "POST":
        data, errors = validate_book_form(request.form)
        if errors:
            return render_template(
                "book_form.html",
                form=request.form,
                errors=errors,
                status_options=STATUS_OPTIONS,
                page_title="Редактировать книгу",
            ), 400
        update_book(book_id, data)
        flash("Изменения сохранены.")
        return redirect(url_for("main.book_detail", book_id=book_id))
    return render_template(
        "book_form.html",
        form=book,
        errors=[],
        status_options=STATUS_OPTIONS,
        page_title="Редактировать книгу",
    )


@bp.route("/books/<int:book_id>/delete", methods=["POST"])
def remove_book(book_id):
    book = get_book(book_id)
    if book is None:
        abort(404)
    delete_book(book_id)
    flash("Книга удалена.")
    return redirect(url_for("main.index"))

