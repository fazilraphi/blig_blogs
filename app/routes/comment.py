from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Comment, Blog

comment_bp = Blueprint("comment", __name__)


@comment_bp.route("/blogs/<int:blog_id>/comments", methods=["POST"])
@jwt_required()
def create_comment(blog_id):
    user_id = int(get_jwt_identity())

    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({"error": "Blog not found"}), 404

    data = request.get_json()
    content = data.get("content")

    if not content:
        return jsonify({"error": "Content is required"}), 400

    new_comment = Comment(
        blog_id=blog_id,
        author_id=user_id,
        content=content
    )

    db.session.add(new_comment)
    db.session.commit()

    return jsonify({
        "message": "Comment added",
        "comment_id": new_comment.id
    }), 201


@comment_bp.route("/blogs/<int:blog_id>/comments", methods=["GET"])
def get_comments(blog_id):
    blog = Blog.query.get(blog_id)
    if not blog:
        return jsonify({"error": "Blog not found"}), 404

    comments = blog.comments

    result = []
    for comment in comments:
        result.append({
            "id": comment.id,
            "content": comment.content,
            "author": {
                "id": comment.author.id,
                "username": comment.author.username
            },
            "created_at": comment.created_at.isoformat()
        })

    return jsonify(result), 200


@comment_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@jwt_required()
def delete_comment(comment_id):
    user_id = int(get_jwt_identity())

    comment = Comment.query.get(comment_id)

    if not comment:
        return jsonify({"error": "Comment not found"}), 404

    if comment.author_id != user_id:
        return jsonify({"error": "Unauthorized"}), 403

    db.session.delete(comment)
    db.session.commit()

    return jsonify({"message": "Comment deleted"}), 200


