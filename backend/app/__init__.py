from pathlib import Path

from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

from .config import Config
from .extensions import db, socketio
from .routes import api_bp


def create_app() -> Flask:
    load_dotenv()

    app = Flask(__name__)
    app.config.from_object(Config)

    Path(app.config["DATA_DIR"]).mkdir(parents=True, exist_ok=True)

    db.init_app(app)

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        supports_credentials=True,
    )

    socketio.init_app(
        app,
        cors_allowed_origins=app.config["CORS_ORIGINS"],
        manage_session=False,
    )

    app.register_blueprint(api_bp)

    @app.get("/health")
    def healthcheck():
        return jsonify({"status": "ok"})

    with app.app_context():
        from . import sockets  # noqa: F401

        db.create_all()

    return app
