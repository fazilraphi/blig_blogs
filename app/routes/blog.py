from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Blog, Like, Media
import cloudinary.uploader

blog_bp = Blueprint("blog", __name__)

# -----------------------------
# CREATE BLOG
# -----------------------------
@blog_bp.route("/blogs", methods=["POST"])
@jwt_required()
def create_blog():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    title = data.get("title")
    body_text = data.get("body_text")

    if not title or not body_text:
        return jsonify({"error": "Missing title or body_text"}), 400

    new_blog = Blog(
        author_id=user_id,
        title=title,
        body_text=body_text,
        is_published=True
    )

    db.session.add(new_blog)
    db.session.commit()

    return jsonify({
        "message": "Blog created successfully",
        "blog_id": new_blog.id
    }), 201


# -----------------------------
# GET ALL BLOGS (PAGINATED)
# -----------------------------
@blog_bp.route("/blogs", methods=["GET"])
def get_all_blogs():
    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    pagination = Blog.query.order_by(
        Blog.created_at.desc()
    ).paginate(page=page, per_page=per_page, error_out=False)

    blogs = pagination.items
    result = []

    for blog in blogs:
        result.append({
            "id": blog.id,
            "title": blog.title,
            "body_text": blog.body_text,
            "likes_count": len(blog.likes),
            "author": {
                "id": blog.author.id,
                "username": blog.author.username
            },
            "media": [
                {
                    "id": m.id,
                    "url": m.media_url,
                    "type": m.media_type
                } for m in blog.media_items
            ],
            "created_at": blog.created_at.isoformat(),
            "updated_at": blog.updated_at.isoformat()
        })

    return jsonify({
        "page": page,
        "per_page": per_page,
        "total": pagination.total,
        "blogs": result
    }), 200


# -----------------------------
# GET SINGLE BLOG
# -----------------------------
@blog_bp.route("/blogs/<int:blog_id>", methods=["GET"])
def get_single_blog(blog_id):
    blog = Blog.query.get(blog_id)

    if not blog:
        return jsonify({"error": "Blog not found"}), 404

    return jsonify({
        "id": blog.id,
        "title": blog.title,
        "body_text": blog.body_text,
        "likes_count": len(blog.likes),
        "author": {
            "id": blog.author.id,
            "username": blog.author.username
        },
        "media": [
            {
                "id": m.id,
                "url": m.media_url,
                "type": m.media_type
            } for m in blog.media_items
        ],
        "created_at": blog.created_at.isoformat(),
        "updated_at": blog.updated_at.isoformat()
    }), 200


# -----------------------------
# UPDATE BLOG
# -----------------------------
@blog_bp.route("/blogs/<int:blog_id>", methods=["PUT"])
@jwt_required()
def update_blog(blog_id):
    user_id = int(get_jwt_identity())
    blog = Blog.query.get(blog_id)

    if not blog:
        return jsonify({"error": "Blog not found"}), 404

    if blog.author_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    data = request.get_json()

    if data.get("title"):
        blog.title = data["title"]

    if data.get("body_text"):
        blog.body_text = data["body_text"]

    db.session.commit()

    return jsonify({
        "message": "Blog updated successfully",
        "blog_id": blog.id
    }), 200


# -----------------------------
# DELETE BLOG
# -----------------------------
@blog_bp.route("/blogs/<int:blog_id>", methods=["DELETE"])
@jwt_required()
def delete_blog(blog_id):
    user_id = int(get_jwt_identity())
    blog = Blog.query.get(blog_id)

    if not blog:
        return jsonify({"error": "Blog not found"}), 404

    if blog.author_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(blog)
    db.session.commit()

    return jsonify({"message": "Blog deleted successfully"}), 200


# -----------------------------
# LIKE BLOG
# -----------------------------
@blog_bp.route("/blogs/<int:blog_id>/like", methods=["POST"])
@jwt_required()
def like_blog(blog_id):
    user_id = int(get_jwt_identity())
    blog = Blog.query.get(blog_id)

    if not blog:
        return jsonify({"error": "Blog not found"}), 404

    existing_like = Like.query.filter_by(
        user_id=user_id,
        blog_id=blog_id
    ).first()

    if existing_like:
        return jsonify({"error": "Already liked"}), 400

    new_like = Like(user_id=user_id, blog_id=blog_id)

    db.session.add(new_like)
    db.session.commit()

    return jsonify({"message": "Blog liked"}), 200


# -----------------------------
# UNLIKE BLOG
# -----------------------------
@blog_bp.route("/blogs/<int:blog_id>/like", methods=["DELETE"])
@jwt_required()
def unlike_blog(blog_id):
    user_id = int(get_jwt_identity())

    like = Like.query.filter_by(
        user_id=user_id,
        blog_id=blog_id
    ).first()

    if not like:
        return jsonify({"error": "Like not found"}), 404

    db.session.delete(like)
    db.session.commit()

    return jsonify({"message": "Blog unliked"}), 200


# -----------------------------
# UPLOAD MEDIA
# -----------------------------
@blog_bp.route("/blogs/<int:blog_id>/media", methods=["POST"])
@jwt_required()
def upload_media(blog_id):
    user_id = int(get_jwt_identity())
    blog = Blog.query.get(blog_id)

    if not blog:
        return jsonify({"error": "Blog not found"}), 404

    if blog.author_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]

    # Optional file size validation (10MB)
    if file.content_length and file.content_length > 10 * 1024 * 1024:
        return jsonify({"error": "File too large"}), 400

    upload_result = cloudinary.uploader.upload(
        file,
        resource_type="auto"
    )

    media_type = (
        "video" if upload_result["resource_type"] == "video" else "image"
    )

    existing_count = Media.query.filter_by(blog_id=blog_id).count()

    new_media = Media(
        blog_id=blog_id,
        uploader_id=user_id,
        media_type=media_type,
        media_url=upload_result["secure_url"],
        thumbnail_url=upload_result.get("thumbnail_url"),
        position=existing_count
    )

    db.session.add(new_media)
    db.session.commit()

    return jsonify({
        "message": "Media uploaded successfully",
        "media_id": new_media.id,
        "media_url": new_media.media_url,
        "media_type": new_media.media_type
    }), 201
