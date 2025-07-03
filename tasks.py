from celery_app import celery_app
import time


@celery_app.task(name="notify_note_created")
def notify_note_created(username:str,note_title:str):
    """Sending mail.."""

    time.sleep(2)
    print(f"[x] Nofitication:'{note_title}' created by {username}")
    return True