import uuid
from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint

from .extensions import db


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Poll(db.Model):
    __tablename__ = "polls"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)

    options = db.relationship(
        "PollOption",
        backref="poll",
        cascade="all, delete-orphan",
        order_by="PollOption.created_at",
        lazy=True,
    )


class PollOption(db.Model):
    __tablename__ = "poll_options"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    poll_id = db.Column(db.String(36), db.ForeignKey("polls.id", ondelete="CASCADE"), nullable=False)
    text = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)


class Vote(db.Model):
    __tablename__ = "votes"
    __table_args__ = (
        UniqueConstraint("poll_id", "voter_token_hash", name="uq_vote_poll_voter"),
        UniqueConstraint("poll_id", "ip_hash", name="uq_vote_poll_ip"),
    )

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    poll_id = db.Column(db.String(36), db.ForeignKey("polls.id", ondelete="CASCADE"), nullable=False)
    option_id = db.Column(db.String(36), db.ForeignKey("poll_options.id", ondelete="CASCADE"), nullable=False)

    voter_token_hash = db.Column(db.String(64), nullable=False)
    ip_hash = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utcnow)
