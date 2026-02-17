from datetime import datetime, timezone

from flask import current_app
from sqlalchemy import func, or_

from .extensions import db
from .models import Poll, PollOption, Vote


def _to_utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def validate_poll_input(question: object, options: object) -> tuple[str, list[str]]:
    clean_question = str(question or "").strip()
    if not clean_question:
        raise ValueError("Question is required.")
    if len(clean_question) > 500:
        raise ValueError("Question is too long. Max 500 characters.")

    if not isinstance(options, list):
        raise ValueError("Options must be a list.")

    clean_options = [str(option).strip() for option in options if str(option).strip()]

    if len(clean_options) < 2:
        raise ValueError("At least 2 non-empty options are required.")
    if len(clean_options) > 10:
        raise ValueError("At most 10 options are allowed.")
    if any(len(option) > 200 for option in clean_options):
        raise ValueError("Each option must be at most 200 characters.")

    lowered = [option.lower() for option in clean_options]
    if len(set(lowered)) != len(lowered):
        raise ValueError("Options must be unique.")

    return clean_question, clean_options


def create_poll(question: str, options: list[str]) -> Poll:
    poll = Poll(question=question)
    for option_text in options:
        poll.options.append(PollOption(text=option_text))

    db.session.add(poll)
    db.session.commit()
    return poll


def get_vote_counts(poll_id: str) -> dict[str, int]:
    rows = (
        db.session.query(Vote.option_id, func.count(Vote.id))
        .filter(Vote.poll_id == poll_id)
        .group_by(Vote.option_id)
        .all()
    )
    return {option_id: count for option_id, count in rows}


def serialize_poll(poll: Poll) -> dict:
    vote_counts = get_vote_counts(poll.id)
    options_payload = [
        {
            "id": option.id,
            "text": option.text,
            "votes": int(vote_counts.get(option.id, 0)),
        }
        for option in poll.options
    ]

    total_votes = sum(option["votes"] for option in options_payload)

    return {
        "id": poll.id,
        "question": poll.question,
        "createdAt": _to_utc_iso(poll.created_at),
        "totalVotes": total_votes,
        "options": options_payload,
    }


def share_url_for_poll(poll_id: str) -> str:
    return f"{current_app.config['FRONTEND_BASE_URL']}/poll/{poll_id}"


def find_viewer_vote(poll_id: str, voter_token_hash: str, ip_hash: str) -> Vote | None:
    return (
        Vote.query.filter(Vote.poll_id == poll_id)
        .filter(
            or_(
                Vote.voter_token_hash == voter_token_hash,
                Vote.ip_hash == ip_hash,
            )
        )
        .first()
    )


def build_poll_response(poll: Poll, viewer_vote: Vote | None) -> dict:
    return {
        "poll": serialize_poll(poll),
        "shareUrl": share_url_for_poll(poll.id),
        "viewer": {
            "hasVoted": viewer_vote is not None,
            "votedOptionId": viewer_vote.option_id if viewer_vote else None,
        },
    }
