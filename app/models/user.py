from datetime import datetime
from app.extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.BigInteger, primary_key=True)

    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)

    bio = db.Column(db.Text, nullable=True)
    profile_image_url = db.Column(db.String(500), nullable=True)
    profile_image_public_id = db.Column(db.String(255), nullable=True)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    blogs = db.relationship(
        "Blog",
        back_populates="author",
        cascade="all, delete-orphan"
    )

    media_uploads = db.relationship(
        "Media",
        back_populates="uploader",
        cascade="all, delete-orphan"
    )

    likes = db.relationship(
        "Like",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    followers = db.relationship(
    "Follow",
    foreign_keys="[Follow.following_id]",
    cascade="all, delete-orphan"
    )

    following = db.relationship(
    "Follow",
    foreign_keys="[Follow.follower_id]",
    cascade="all, delete-orphan"
    )
    comments = db.relationship(
    "Comment",
    back_populates="author",
    cascade="all, delete-orphan"
    )


    def __repr__(self):
        return f"<User {self.username}>"
