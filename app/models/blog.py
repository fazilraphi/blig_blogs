from datetime import datetime
from app.extensions import db

class Blog(db.Model):
    __tablename__ = "blogs"

    id = db.Column(db.BigInteger, primary_key=True)

    author_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    title = db.Column(db.String(255), nullable=False)
    body_text = db.Column(db.Text, nullable=False)

    is_published = db.Column(db.Boolean, default=False)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )

    # Relationships
    author = db.relationship("User", back_populates="blogs")

    media_items = db.relationship(
        "Media",
        back_populates="blog",
        cascade="all, delete-orphan",
        order_by="Media.position"
    )

    likes = db.relationship(
        "Like",
        back_populates="blog",
        cascade="all, delete-orphan"
    )

    comments = db.relationship(
    "Comment",
    back_populates="blog",
    cascade="all, delete-orphan",
    order_by="Comment.created_at.asc()"
    )

    def __repr__(self):
        return f"<Blog {self.id} {self.title}>"
