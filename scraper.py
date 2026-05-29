import requests
from bs4 import BeautifulSoup
from app import db, Book

base_url = "https://books.toscrape.com/catalogue/page-{}.html"

def scrape_books():
    for page in range(1, 3):  # sonra 50 yaparsın
        url = base_url.format(page)
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        books = soup.find_all("article", class_="product_pod")

        for book in books:
            title = book.h3.a["title"]

            price = book.find("p", class_="price_color").text
            price = float(price.replace("£", "").replace("Â", "").strip())

            rating_map = {
                "One": 1,
                "Two": 2,
                "Three": 3,
                "Four": 4,
                "Five": 5
            }

            rating_class = book.p["class"][1]
            rating = rating_map.get(rating_class, 0)

            # 🚀 DUPLICATE CONTROL (çok önemli)
            exists = Book.query.filter_by(title=title).first()
            if exists:
                continue

            # 💾 DATABASE INSERT
            new_book = Book(
                title=title,
                price=price,
                rating=rating
            )

            db.session.add(new_book)

    db.session.commit()
    print("Scraping + DB insert completed ✔")


if __name__ == "__main__":
    from app import app

    with app.app_context():
        scrape_books()