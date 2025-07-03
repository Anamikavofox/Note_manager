from celery import Celery

REDIS_URL="redis://localhost:6379/0"


celery_app=Celery("Notes_worker",
                  broker=REDIS_URL,
                  backend=REDIS_URL)


celery_app.conf.update(task_serializer="json",
                       result_serializer="json",
                       accept_content=["json"],
                       task_track_started=True,
                       task_time_limit=30)

celery_app.conf.imports = ["tasks"]

