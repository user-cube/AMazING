from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
import requests

from models import Experience
from schedule.config_experience import start_experience


def schedule_next_experience(db):
    date_now = datetime.now()

    experience_scheduled = db.session.query(Experience) \
        .filter(Experience.begin_date >= date_now) \
        .order_by(Experience.begin_date.asc()) \
        .one()
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=running_next_experience, trigger='date', run_date=experience_scheduled.begin_date, args=experience_scheduled.id)
    scheduler.add_job(func=ending_next_experience, trigger='date', run_date=experience_scheduled.end_date, args=experience_scheduled.id)
    scheduler.start()
    print(scheduler.get_jobs())

def running_next_experience(id):
    try:
        start_experience(id)
    except NoResultFound:
    except

def ending_next_experience(id):

