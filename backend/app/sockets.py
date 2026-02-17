from flask_socketio import emit, join_room, leave_room

from .extensions import socketio
from .models import Poll
from .services import serialize_poll


@socketio.on("join_poll")
def handle_join_poll(payload):
    poll_id = (payload or {}).get("pollId")
    if not poll_id:
        emit("socket_error", {"error": "pollId is required."})
        return

    room = f"poll:{poll_id}"
    join_room(room)

    poll = Poll.query.get(poll_id)
    if not poll:
        emit("socket_error", {"error": "Poll not found."})
        return

    emit("poll_updated", serialize_poll(poll))


@socketio.on("leave_poll")
def handle_leave_poll(payload):
    poll_id = (payload or {}).get("pollId")
    if not poll_id:
        return
    leave_room(f"poll:{poll_id}")
