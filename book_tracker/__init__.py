from flask import Flask

from .db import init_app
from .routes import bp


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
        DATABASE=app.instance_path + "/book_tracker.sqlite",
    )

    if test_config is not None:
        app.config.update(test_config)

    init_app(app)
    app.register_blueprint(bp)

    with app.app_context():
        from .db import init_db

        init_db()

    return app

