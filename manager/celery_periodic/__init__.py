from celery import Celery

celery = None

environment_phase_dict = {
    "production": "config.ProdConfig",
    "development": "config.DevConfig",
    "testing": "config.TestConfig",
}


def make_celery(main_flask_app):
    """This method generates the celery object for the Flask app one"""

    celery = Celery(main_flask_app.import_name, include=["manager.celery_periodic.tasks"])

    celery.config_from_object(environment_phase_dict.get(main_flask_app.config.get("ENV"), "config.DevConfig"))

    task_base = celery.Task

    class ContextTask(task_base):
        abstract = True

        def __call__(self, *args, **kwargs):
            with main_flask_app.app_context():
                return task_base.__call__(self, *args, **kwargs)

    celery.Task = ContextTask

    return celery
