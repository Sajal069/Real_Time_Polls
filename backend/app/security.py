import hashlib
import secrets

from flask import current_app, request
from itsdangerous import BadSignature, URLSafeSerializer

COOKIE_SALT = "poll-voter-cookie"


def _serializer() -> URLSafeSerializer:
    return URLSafeSerializer(current_app.config["SECRET_KEY"], salt=COOKIE_SALT)


def get_or_create_voter_token() -> tuple[str, bool]:
    cookie_name = current_app.config["COOKIE_NAME"]
    signed_cookie = request.cookies.get(cookie_name)

    if signed_cookie:
        try:
            payload = _serializer().loads(signed_cookie)
            token = payload.get("token") if isinstance(payload, dict) else None
            if isinstance(token, str) and token.strip():
                return token, False
        except BadSignature:
            pass

    return secrets.token_urlsafe(24), True


def set_voter_cookie(response, token: str) -> None:
    signed_cookie = _serializer().dumps({"token": token})

    response.set_cookie(
        key=current_app.config["COOKIE_NAME"],
        value=signed_cookie,
        max_age=current_app.config["COOKIE_MAX_AGE"],
        secure=current_app.config["COOKIE_SECURE"],
        httponly=True,
        samesite=current_app.config["COOKIE_SAMESITE"],
    )


def hash_voter_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def get_client_ip() -> str:
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.remote_addr or "0.0.0.0"


def hash_ip(ip_address: str) -> str:
    salted_ip = f"{current_app.config['IP_HASH_SALT']}:{ip_address}"
    return hashlib.sha256(salted_ip.encode("utf-8")).hexdigest()
