from datetime import datetime
from app.extensions import db

class Like(db.Model):
    __tablename__ = "likes"

    id = db.Column(db.BigInteger, primary_key=True)

    user_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    blog_id = db.Column(
        db.BigInteger,
        db.ForeignKey("blogs.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "blog_id", name="uq_user_blog_like"),
    )

    # Relationships
    user = db.relationship("User", back_populates="likes")
    blog = db.relationship("Blog", back_populates="likes")

    def __repr__(self):
        return f"<Like user={self.user_id} blog={self.blog_id}>"
