from celery import Celery


def make_celery(_app):
    _celery = Celery(_app.import_name,
                     backend=_app.config['CELERY_RESULT_BACKEND'],
                     broker=_app.config['CELERY_BROKER_URL'])
    _celery.conf.update(_app.config)
    TaskBase = _celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with _app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    _celery.Task = ContextTask
    return _celery
