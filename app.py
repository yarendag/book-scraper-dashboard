from flask import Flask
from models import db, User

from flask_login import LoginManager

# Blueprints
from routes.books import books_bp
from routes.auth import auth

app = Flask(__name__)

# =========================
# CONFIG
# =========================
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///books.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = "supersecretkey"

# =========================
# DB INIT
# =========================
db.init_app(app)

# =========================
# LOGIN SYSTEM
# =========================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"

# ⚠️ SQLAlchemy 2.x FIX (important)
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


# =========================
# BLUEPRINT REGISTER
# =========================
app.register_blueprint(books_bp)
app.register_blueprint(auth)

# =========================
# DB CREATE + RUN
# =========================
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("App started ✔ (Full Modular System)")

    app.run(debug=True)