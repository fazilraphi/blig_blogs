from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models import Follow, User

follow_bp = Blueprint("follow", __name__)
@follow_bp.route("/users/<int:user_id>/follow", methods=["POST"])
@jwt_required()
def follow_user(user_id):
    current_user_id = int(get_jwt_identity())

    if current_user_id == user_id:
        return jsonify({"error": "You cannot follow yourself"}), 400

    user_to_follow = User.query.get(user_id)
    if not user_to_follow:
        return jsonify({"error": "User not found"}), 404

    existing_follow = Follow.query.filter_by(
        follower_id=current_user_id,
        following_id=user_id
    ).first()

    if existing_follow:
        return jsonify({"error": "Already following"}), 400

    new_follow = Follow(
        follower_id=current_user_id,
        following_id=user_id
    )

    db.session.add(new_follow)
    db.session.commit()

    return jsonify({"message": "Followed successfully"}), 200


@follow_bp.route("/users/<int:user_id>/follow", methods=["DELETE"])
@jwt_required()
def unfollow_user(user_id):
    current_user_id = int(get_jwt_identity())

    follow = Follow.query.filter_by(
        follower_id=current_user_id,
        following_id=user_id
    ).first()

    if not follow:
        return jsonify({"error": "Not following"}), 404

    db.session.delete(follow)
    db.session.commit()

    return jsonify({"message": "Unfollowed successfully"}), 200

@follow_bp.route("/users/<int:user_id>/followers", methods=["GET"])
def get_followers(user_id):
    followers = Follow.query.filter_by(following_id=user_id).all()

    result = []
    for follow in followers:
        user = User.query.get(follow.follower_id)
        result.append({
            "id": user.id,
            "username": user.username
        })

    return jsonify(result), 200


@follow_bp.route("/users/<int:user_id>/following", methods=["GET"])
def get_following(user_id):
    following = Follow.query.filter_by(follower_id=user_id).all()

    result = []
    for follow in following:
        user = User.query.get(follow.following_id)
        result.append({
            "id": user.id,
            "username": user.username
        })

    return jsonify(result), 200

