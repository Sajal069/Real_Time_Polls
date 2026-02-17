from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError

from .extensions import db, socketio
from .models import Poll, PollOption, Vote
from .security import (
    get_client_ip,
    get_or_create_voter_token,
    hash_ip,
    hash_voter_token,
    set_voter_cookie,
)
from .services import (
    build_poll_response,
    create_poll,
    find_viewer_vote,
    serialize_poll,
    validate_poll_input,
)

api_bp = Blueprint("api", __name__, url_prefix="/api")


@api_bp.post("/polls")
def create_poll_route():
    payload = request.get_json(silent=True) or {}

    try:
        question, options = validate_poll_input(payload.get("question"), payload.get("options"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    poll = create_poll(question, options)

    voter_token, is_new_token = get_or_create_voter_token()
    voter_hash = hash_voter_token(voter_token)
    ip_hash = hash_ip(get_client_ip())

    viewer_vote = find_viewer_vote(poll.id, voter_hash, ip_hash)
    response_payload = build_poll_response(poll, viewer_vote)

    response = jsonify(response_payload)
    if is_new_token:
        set_voter_cookie(response, voter_token)
    return response, 201


@api_bp.get("/polls/<poll_id>")
def get_poll_route(poll_id: str):
    poll = Poll.query.get(poll_id)
    if not poll:
        return jsonify({"error": "Poll not found."}), 404

    voter_token, is_new_token = get_or_create_voter_token()
    voter_hash = hash_voter_token(voter_token)
    ip_hash = hash_ip(get_client_ip())

    viewer_vote = find_viewer_vote(poll.id, voter_hash, ip_hash)
    response_payload = build_poll_response(poll, viewer_vote)

    response = jsonify(response_payload)
    if is_new_token:
        set_voter_cookie(response, voter_token)
    return response


@api_bp.post("/polls/<poll_id>/vote")
def vote_route(poll_id: str):
    poll = Poll.query.get(poll_id)
    if not poll:
        return jsonify({"error": "Poll not found."}), 404

    payload = request.get_json(silent=True) or {}
    option_id = str(payload.get("optionId") or "").strip()
    if not option_id:
        return jsonify({"error": "optionId is required."}), 400

    option = PollOption.query.filter_by(id=option_id, poll_id=poll_id).first()
    if not option:
        return jsonify({"error": "Invalid option for this poll."}), 400

    voter_token, is_new_token = get_or_create_voter_token()
    voter_hash = hash_voter_token(voter_token)
    ip_hash = hash_ip(get_client_ip())

    already_voted_by_token = Vote.query.filter_by(
        poll_id=poll_id,
        voter_token_hash=voter_hash,
    ).first()
    if already_voted_by_token:
        response = jsonify({"error": "This browser has already voted in this poll."})
        if is_new_token:
            set_voter_cookie(response, voter_token)
        return response, 409

    already_voted_by_ip = Vote.query.filter_by(
        poll_id=poll_id,
        ip_hash=ip_hash,
    ).first()
    if already_voted_by_ip:
        response = jsonify({"error": "A vote from this IP/network has already been recorded for this poll."})
        if is_new_token:
            set_voter_cookie(response, voter_token)
        return response, 409

    db.session.add(
        Vote(
            poll_id=poll_id,
            option_id=option_id,
            voter_token_hash=voter_hash,
            ip_hash=ip_hash,
        )
    )

    try:
        db.session.commit()
    except IntegrityError as exc:
        db.session.rollback()
        error_text = str(exc.orig).lower()
        if "ip_hash" in error_text:
            message = "A vote from this IP/network has already been recorded for this poll."
        else:
            message = "This browser has already voted in this poll."
        response = jsonify({"error": message})
        if is_new_token:
            set_voter_cookie(response, voter_token)
        return response, 409

    poll_payload = serialize_poll(poll)
    socketio.emit("poll_updated", poll_payload, to=f"poll:{poll.id}")

    viewer_vote = find_viewer_vote(poll.id, voter_hash, ip_hash)
    response_payload = build_poll_response(poll, viewer_vote)

    response = jsonify(response_payload)
    if is_new_token:
        set_voter_cookie(response, voter_token)
    return response, 201
