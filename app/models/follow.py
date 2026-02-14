from datetime import datetime
from app.extensions import db

class Follow(db.Model):
    __tablename__ = "follows"

    id = db.Column(db.BigInteger, primary_key=True)

    follower_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    following_id = db.Column(
        db.BigInteger,
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    __table_args__ = (
        db.UniqueConstraint(
            "follower_id",
            "following_id",
            name="uq_follower_following"
        ),
    )

    def __repr__(self):
        return f"<Follow {self.follower_id} -> {self.following_id}>"
