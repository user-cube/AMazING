from datetime import datetime
import logging

import apscheduler
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask
from flask_mail import Mail, Message
from flask_sqlalchemy import SQLAlchemy

from sqlalchemy.orm.exc import NoResultFound

from models import Experience, Profile
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
    mail: Mail = None

    scheduler_end = BackgroundScheduler()
    scheduler_start = BackgroundScheduler()

    def __init__(self):
        pass

    def configure(self, app, db):
        self.app = app
        self.db = db
        self.mail = Mail(self.app)

    def manage_next_experience(self, new_experience=None):
        with self.app.app_context():
            date_now = datetime.now()
            experience_scheduled = self.db.session.query(Experience) \
                .filter(Experience.begin_date >= date_now) \
                .order_by(Experience.begin_date.asc()) \
                .first()
        if not experience_scheduled:
            self.app.logger.info('ExperienceSchedule: No Next Experience Found')
            return

                # If inserted experiencce not the next one, no changed are needed
        if new_experience and experience_scheduled.id != new_experience:
            return
        self.app.logger.info(f'Adding New Experience {experience_scheduled.serializable}')
        self.remove_schedule_experience(experience_scheduled)
        self.insert_job(experience_scheduled)
        self.start_jobs()

    def running_next_experience(self, experience):
        try:
            self.app.logger.info(f'Starting to run Experience {experience.id} - {experience.name}')
            start_experience(experience.id, self.app, self.db)
            self.starting_experience_mail(experience)

        except FailedExperienceException as err:
            logging.error(f'ExperienceSchedule: {err.messages}')
            self.scheduler_end.remove_job(str(experience.id))
            self.failing_experience_mail(experience)
        except Exception as err:
            self.app.logger.error('ExperienceSchedule:' + err.__str__())
        self.manage_next_experience()

    def ending_experience(self, experience):
        try:
            response = finish_experience(experience.id, self.app, self.db)
            self.app.logger.info(f'ExperienceSchedule: Finished Experience {experience.id}, APUs: {[apu_response for apu_response in response]}')
            self.finishing_experience_mail(experience, response)
        except NoResultFound:
            self.app.logger.error(f'ExperienceSchedule: No Experience Found, Experience {experience}, id {experience.id}')

    def insert_job(self, experience_scheduled):
        self.scheduler_start.add_job(id=str(experience_scheduled.id),
                                     func=self.running_next_experience,
                                     trigger='date',
                                     run_date=experience_scheduled.begin_date,
                                     args=(experience_scheduled,))

        self.scheduler_end.add_job(id=str(experience_scheduled.id),
                                   func=self.ending_experience,
                                   trigger='date',
                                   run_date=experience_scheduled.end_date,
                                   args=(experience_scheduled,))

    def remove_schedule_experience(self, experience):
        if job_has_item(str(experience.id), self.scheduler_start.get_jobs()):
            self.scheduler_start.remove_job(str(experience.id))
        if job_has_item(str(experience.id), self.scheduler_end.get_jobs()):
            self.scheduler_end.remove_job(str(experience.id))

    def start_jobs(self):
        self.app.logger.info('starting Jobs')
        if not self.scheduler_start.state == apscheduler.schedulers.base.STATE_RUNNING:
            self.scheduler_start.start()
        if not self.scheduler_end.state == apscheduler.schedulers.base.STATE_RUNNING:
            self.scheduler_end.start()

    def starting_experience_mail(self, experience):
        with self.app.app_context():
            author = self.db.session.query(Profile).get(experience.profile)
            msg = Message(recipients=[author.email])
            msg.subject = f'[AMazING Playground] Experience {experience.id} - {experience.name} Started running'
            msg.body = f"""\
            Dear {author.name}, 
            
            Your scheduled experience {experience.id} - '{experience.name}' has just started. 
            
            The ending is scheduled to {experience.end_date.strftime("%Y-%m-%d %H:%M:%S")}.
            
            Kind regards,"""

            msg.sender = (self.app.config['MAIL_DEFAULT_SENDER'], self.app.config['MAIL_USERNAME'])
            self.mail.send(msg)

    def finishing_experience_mail(self, experience, response: list):
        with self.app.app_context():
            author = self.db.session.query(Profile).get(experience.profile)
            msg = Message(recipients=[author.email])
            msg.subject = f'[AMazING Playground]Experience {experience.id} - {experience.name} Finished successfully'
            msg.body = f"""\
            Dear {author.name}, 
            
            'Your scheduled experience {experience.id} - '{experience.name}' has finished, you can check the results on this link: http://localhost:8000/checkTests/{experience.id}.
                
            Kind regards,"""

            msg.sender = (self.app.config['MAIL_DEFAULT_SENDER'], self.app.config['MAIL_USERNAME'])
            self.mail.send(msg)

    def failing_experience_mail(self, experience):
        with self.app.app_context():
            author = self.db.session.query(Profile).get(experience.profile)
            msg = Message(recipients=[author.email])
            msg.subject = f'[AMazING Playground] Experience {experience.id} - {experience.name} Failed running'
            msg.body = f"""\
            Dear {author.name}, 
            
            Your scheduled experience {experience.id} - '{experience.name}' failed runing, you can verify the details on this link: http://localhost:8000/checkTests/{experience.id}.

            Kind regards,"""

            msg.sender = (self.app.config['MAIL_DEFAULT_SENDER'], self.app.config['MAIL_USERNAME'])
            self.mail.send(msg)


experience_scheduler_manager = ExperienceSchedulerManager()
