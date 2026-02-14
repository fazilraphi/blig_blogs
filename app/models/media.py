from datetime import datetime
from app.extensions import db


class Media(db.Model):
    __tablename__ = "media"

    id = db.Column(db.BigInteger, primary_key=True)

    blog_id = db.Column(
        db.BigInteger,
        db.ForeignKey("blogs.id", ondelete="CASCADE"),
        nullable=False
    )

    uploader_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    # ✅ FIXED
    media_type = db.Column(db.String(20), nullable=False)

    media_url = db.Column(db.String(500), nullable=False)
    thumbnail_url = db.Column(db.String(500), nullable=True)

    position = db.Column(db.Integer, default=0)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    # Relationships
    blog = db.relationship("Blog", back_populates="media_items")
    uploader = db.relationship("User", back_populates="media_uploads")

    def __repr__(self):
        return f"<Media {self.media_type} {self.id}>"
