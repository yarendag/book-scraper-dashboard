from flask import Blueprint, jsonify, request
from models import Book

api = Blueprint("api", __name__)

@api.route("/api/books")
def get_books():

    page = request.args.get("page", 1, type=int)
    per_page = 10

    pagination = Book.query.paginate(page=page, per_page=per_page)

    return jsonify({
        "total": pagination.total,
        "page": page,
        "data": [
            {
                "title": b.title,
                "price": b.price,
                "rating": b.rating
            }
            for b in pagination.items
        ]
    })