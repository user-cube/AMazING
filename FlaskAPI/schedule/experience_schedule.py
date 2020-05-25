from datetime import datetime
import logging

import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.orm.exc import NoResultFound

from models import Experience
from schedule.config_experience import start_experience, finish_experience
from views.base import FailedExperienceException


def job_has_item(id: str, list: list):
    for item in list:
        if item.id == id:
            return True
    return False


class ExperienceSchedulerManager:
    app: Flask = None
    db: SQLAlchemy = None

    scheduler_end = BackgroundScheduler()
    scheduler_start = BackgroundScheduler()

    def __init__(self):
        pass

    def configure(self, app, db):
        self.app = app
        self.db = db

    def manage_next_experience(self, new_experience=None):
        with self.app.app_context():
            date_now = datetime.now()
            experience_scheduled = self.db.session.query(Experience) \
                .filter(Experience.begin_date >= date_now) \
                .order_by(Experience.begin_date.asc()) \
                .first()
            if not experience_scheduled:
                logging.info('ExperienceSchedule: No Next Experience Found')
                return

                                            # If inserted experiencce not the next one, no changed are needed
            if new_experience and experience_scheduled.id != new_experience:
                return

            self.remove_schedule_experience(id)
            self.insert_job(experience_scheduled)
            self.start_jobs()

    def running_next_experience(self, id):
        try:
            start_experience(id, self.app, self.db)
        except NoResultFound:
            logging.error(f'ExperienceSchedule: No Experience Found, Experience.id {id}')
            self.scheduler_end.remove_job(str(id))
        except FailedExperienceException as err:
            print('\n\n\n\nNEXT: ')
            print(self.scheduler_start.get_jobs())
            print(self.scheduler_end.get_jobs())
            logging.error(f'ExperienceSchedule: {err.messages}')
            self.scheduler_end.remove_job(str(id))
        self.manage_next_experience()

    def ending_next_experience(self, id):
        try:
            response = finish_experience(id, self.app, self.db)
            print('\n\n\n', f'ExperienceSchedule: Finished Experience {id}, APUs: {[apu_response for apu_response in response]}')
            logging.info(f'ExperienceSchedule: Finished Experience {id}, APUs: {[apu_response for apu_response in response]}')
        except NoResultFound:
            print('\n\n\n', f'ExperienceSchedule: No Experience Found, Experience.id {id}')
            logging.error(f'ExperienceSchedule: No Experience Found, Experience.id {id}')

    def insert_job(self, experience_scheduled):
        self.scheduler_start.add_job(id=str(experience_scheduled.id),
                                     func=self.running_next_experience,
                                     trigger='date',
                                     run_date=experience_scheduled.begin_date,
                                     args=(experience_scheduled.id,))

        self.scheduler_end.add_job(id=str(experience_scheduled.id),
                                   func=self.ending_next_experience,
                                   trigger='date',
                                   run_date=experience_scheduled.end_date,
                                   args=(experience_scheduled.id,))

    def remove_schedule_experience(self, id):
        if job_has_item(str(id), self.scheduler_start.get_jobs()):
            self.scheduler_start.remove_job(str(id))
        if job_has_item(str(id), self.scheduler_end.get_jobs()):
            self.scheduler_end.remove_job(str(id))

    def start_jobs(self):
        if not self.scheduler_start.state == apscheduler.schedulers.base.STATE_RUNNING:
            self.scheduler_start.start()
        if not self.scheduler_end.state == apscheduler.schedulers.base.STATE_RUNNING:
            self.scheduler_end.start()


experience_scheduler_manager = ExperienceSchedulerManager()
