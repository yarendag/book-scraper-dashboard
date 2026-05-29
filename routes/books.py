from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Book, db, Favorite
import plotly.express as px

books_bp = Blueprint("books", __name__)

# =========================
# HOME ROUTE
# =========================
@books_bp.route("/")
def home():

    query = request.args.get("q")
    filter_type = request.args.get("filter")

    page = request.args.get("page", 1, type=int)
    per_page = 10

    books_query = Book.query

    # SEARCH
    if query:
        books_query = books_query.filter(Book.title.ilike(f"%{query}%"))

    # FILTERS
    if filter_type == "cheap":
        books_query = books_query.filter(Book.price < 20)

    elif filter_type == "expensive":
        books_query = books_query.filter(Book.price >= 20)

    elif filter_type == "top":
        books_query = books_query.filter(Book.rating >= 4)

    pagination = books_query.paginate(page=page, per_page=per_page)

    books_list = pagination.items
    total_books = pagination.total
    pages = pagination.pages   # ✅ pagination UI için eklendi

    avg_price = round(
        sum(b.price for b in books_list) / len(books_list),
        2
    ) if books_list else 0

    top_books = sorted(books_list, key=lambda x: x.price, reverse=True)

    prices = [b.price for b in books_list]
    ratings = [b.rating for b in books_list]

    if books_list:

        fig_price = px.histogram(
            x=prices,
            nbins=15,
            title="Price Distribution"
        )
        price_chart = fig_price.to_html(full_html=False)

        rating_counts = {}
        for r in ratings:
            rating_counts[r] = rating_counts.get(r, 0) + 1

        fig_rating = px.bar(
            x=list(rating_counts.keys()),
            y=list(rating_counts.values()),
            title="Rating Distribution"
        )
        rating_chart = fig_rating.to_html(full_html=False)

    else:
        price_chart = "<p>No data</p>"
        rating_chart = "<p>No data</p>"

    return render_template(
        "index.html",
        total_books=total_books,
        avg_price=avg_price,
        tables=[
            {"id": b.id, "title": b.title, "price": b.price, "rating": b.rating}
            for b in top_books
        ],
        query=query,
        page=page,
        pages=pages,  # ✅ pagination UI
        has_next=pagination.has_next,
        has_prev=pagination.has_prev,
        price_chart=price_chart,
        rating_chart=rating_chart
    )


# =========================
# FAVORITE ADD
# =========================
@books_bp.route("/favorite/<int:book_id>")
@login_required
def favorite(book_id):

    existing = Favorite.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()

    if not existing:
        fav = Favorite(user_id=current_user.id, book_id=book_id)
        db.session.add(fav)
        db.session.commit()

        flash("Book saved to library ❤️")

    return redirect(url_for("books.home"))


# =========================
# FAVORITE REMOVE
# =========================
@books_bp.route("/remove_favorite/<int:book_id>")
@login_required
def remove_favorite(book_id):

    fav = Favorite.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).first()

    if fav:
        db.session.delete(fav)
        db.session.commit()

        flash("Book removed ❌")

    return redirect(url_for("books.library"))


# =========================
# MY LIBRARY
# =========================
@books_bp.route("/library")
@login_required
def library():

    favorites = Favorite.query.filter_by(
        user_id=current_user.id
    ).all()

    books = [fav.book for fav in favorites]

    return render_template("library.html", books=books)


# =========================
# AUTOCOMPLETE API
# =========================
@books_bp.route("/autocomplete")
def autocomplete():

    query = request.args.get("q", "")

    if not query:
        return jsonify([])

    books = Book.query.filter(
        Book.title.ilike(f"%{query}%")
    ).limit(5).all()

    return jsonify([book.title for book in books])