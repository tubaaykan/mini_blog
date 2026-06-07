import logging
import os

from dotenv import load_dotenv
from flask import Flask, render_template
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import text

from config import CONFIG_MAP
from models import db
from routes import main_bp, posts_bp


csrf = CSRFProtect()


def _setup_logging(app: Flask):
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    app.logger.setLevel(logging.INFO)


def _configure_engine_pool(app: Flask):
    uri = app.config["SQLALCHEMY_DATABASE_URI"]
    if not uri.startswith("sqlite"):
        app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
            "pool_pre_ping": True,
            "pool_size": 5,
            "max_overflow": 10,
        }


def _migrate_legacy_schema(app: Flask):
    with app.app_context():
        db.create_all()
        columns = [
            row[1]
            for row in db.session.execute(text("PRAGMA table_info(posts)")).fetchall()
        ]
        migrations = {
            "image_filename": "ALTER TABLE posts ADD COLUMN image_filename VARCHAR(255)",
            "thumbnail_filename": "ALTER TABLE posts ADD COLUMN thumbnail_filename VARCHAR(255)",
            "image_alt_text": "ALTER TABLE posts ADD COLUMN image_alt_text VARCHAR(120)",
            "created_at": "ALTER TABLE posts ADD COLUMN created_at DATETIME",
            "updated_at": "ALTER TABLE posts ADD COLUMN updated_at DATETIME",
        }

        for column, statement in migrations.items():
            if column not in columns:
                db.session.execute(text(statement))

        db.session.execute(
            text(
                "UPDATE posts SET created_at = COALESCE(created_at, CURRENT_TIMESTAMP), "
                "updated_at = COALESCE(updated_at, CURRENT_TIMESTAMP)"
            )
        )
        db.session.commit()


def create_app(config_name: str | None = None):
    load_dotenv()

    app = Flask(__name__)
    selected = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(CONFIG_MAP.get(selected, CONFIG_MAP["development"]))

    _setup_logging(app)
    _configure_engine_pool(app)

    db.init_app(app)
    csrf.init_app(app)

    app.register_blueprint(main_bp)
    app.register_blueprint(posts_bp)

    _migrate_legacy_schema(app)

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def server_error(error):
        return render_template("500.html"), 500

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=app.config.get("DEBUG", False))
