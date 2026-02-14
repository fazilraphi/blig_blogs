from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models import User, TokenBlocklist
import bcrypt
import cloudinary.uploader

from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)

auth_bp = Blueprint("auth", __name__)

# -------------------------
# REGISTER
# -------------------------
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    existing_user = User.query.filter(
        (User.email == email) | (User.username == username)
    ).first()

    if existing_user:
        return jsonify({"error": "User already exists"}), 400

    hashed_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())

    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_pw.decode("utf-8")
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201


# -------------------------
# LOGIN
# -------------------------
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        return jsonify({"error": "Invalid credentials"}), 401

    if not bcrypt.checkpw(password.encode("utf-8"), user.password_hash.encode("utf-8")):
        return jsonify({"error": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200


# -------------------------
# CURRENT USER
# -------------------------
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "profile_image_url": user.profile_image_url
    }), 200


# -------------------------
# PROFILE IMAGE
# -------------------------
@auth_bp.route("/profile/image", methods=["POST"])
@jwt_required()
def upload_profile_image():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    upload_result = cloudinary.uploader.upload(
        file,
        folder="profile_images",
        resource_type="image"
    )

    user.profile_image_url = upload_result["secure_url"]
    user.profile_image_public_id = upload_result["public_id"]

    db.session.commit()

    return jsonify({
        "message": "Profile image updated",
        "profile_image_url": user.profile_image_url
    }), 200


# -------------------------
# REFRESH TOKEN
# -------------------------
@auth_bp.route("/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    new_access_token = create_access_token(identity=user_id)

    return jsonify({
        "access_token": new_access_token
    }), 200


# -------------------------
# LOGOUT (ACCESS TOKEN)
# -------------------------
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    jti = get_jwt()["jti"]

    revoked_token = TokenBlocklist(jti=jti)
    db.session.add(revoked_token)
    db.session.commit()

    return jsonify({"message": "Successfully logged out"}), 200


# -------------------------
# LOGOUT (REFRESH TOKEN)
# -------------------------
@auth_bp.route("/logout/refresh", methods=["POST"])
@jwt_required(refresh=True)
def logout_refresh():
    jti = get_jwt()["jti"]

    revoked_token = TokenBlocklist(jti=jti)
    db.session.add(revoked_token)
    db.session.commit()

    return jsonify({"message": "Refresh token revoked"}), 200
