from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_httpauth import HTTPBasicAuth
from flask_migrate import Migrate

from manager import celery_periodic


# ------------------------------------------Instantiation of the environment-------------------------------------------
migrate_flask = Migrate()
auth = HTTPBasicAuth()
sql_db = SQLAlchemy()

environment_phase_dict = {
    "development": "config.DevConfig",
    "testing": "config.TestConfig",
    "production": "config.ProdConfig"
}


# ------------------------------------------Builder of the application-------------------------------------------------
def create_app():
    """Builder of the Flask application with every submodules and dependencies"""
    app = Flask(__name__, instance_relative_config=False)

    app.config.from_object(environment_phase_dict.get("testing", "config.DevConfig"))

    sql_db.init_app(app)
    migrate_flask.init_app(app, sql_db)

    celery = celery_periodic.make_celery(app)
    celery_periodic.celery = celery

    app.register_blueprint(app.config.get("SWAGGERUI_BLUEPRINT"), url_prefix=app.config.get("SWAGGER_URL"))

    with app.app_context():
        from . import flask_app_routes

    return app
