from flask import Flask
from app.extensions import db
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from datetime import timedelta
import cloudinary
import os


def create_app():
    app = Flask(__name__)

    # -------------------------
    # CORS CONFIGURATION
    # -------------------------
    CORS(
        app,
        resources={r"/*": {"origins": [
            "http://localhost:3000",                 # local frontend
            "https://blig-frontend.onrender.com"    # your deployed frontend (change if needed)
        ]}},
        supports_credentials=True
    )

    # -------------------------
    # Database Configuration
    # -------------------------
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    # Render fix
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # -------------------------
    # JWT Configuration
    # -------------------------
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(minutes=15)
    app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=7)

    # -------------------------
    # Cloudinary Configuration
    # -------------------------
    cloudinary.config(
        cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
        api_key=os.getenv("CLOUDINARY_API_KEY"),
        api_secret=os.getenv("CLOUDINARY_API_SECRET"),
        secure=True
    )

    # -------------------------
    # Initialize Extensions
    # -------------------------
    db.init_app(app)
    Migrate(app, db)
    jwt = JWTManager(app)

    # -------------------------
    # Token Revocation Check
    # -------------------------
    from app.models import TokenBlocklist

    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        token = TokenBlocklist.query.filter_by(jti=jti).first()
        return token is not None

    # -------------------------
    # Register Blueprints
    # -------------------------
    from app.routes.auth import auth_bp
    from app.routes.blog import blog_bp
    from app.routes.follow import follow_bp
    from app.routes.comment import comment_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(blog_bp)
    app.register_blueprint(follow_bp)
    app.register_blueprint(comment_bp)

    # -------------------------
    # Health Check
    # -------------------------
    @app.route("/")
    def home():
        return {
            "status": "success",
            "message": "Blig Blogs API is running 🚀",
            "version": "1.0"
        }

    return app
