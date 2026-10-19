
import os
from pathlib import Path

from flask import Flask, redirect, render_template, url_for

from database import init_app as init_database_app, init_db


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-only-change-this"),
        DATABASE=os.path.join(app.instance_path, "cafe.sqlite"),
    )

    if test_config is not None:
        app.config.update(test_config)

    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    init_database_app(app)

    with app.app_context():
        init_db()

    @app.route("/")
    def home():
        return render_template("index.html")

    @app.route("/menu")
    def menu():
        return render_template("menu.html")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(debug=True)
