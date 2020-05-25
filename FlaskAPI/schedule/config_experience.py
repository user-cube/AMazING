import requests
from flask_api import status

from models import Experience, APU_Config, APU, ExperienceStatus
from views.base import FailedExperienceException

from sqlalchemy.orm.exc import NoResultFound


def start_experience(id, app, db):
    with app.app_context():

        config_query = db.session.query(APU_Config, APU) \
            .filter(APU_Config.experience == id) \
            .filter(APU_Config.apu == APU.id).all()
        experience = db.session.query(Experience).get(id)
        if not experience:
            raise NoResultFound

            # if no apu config, those lines wont be executed
        for apu_config, apu in config_query:

            json_req = {'experience': id, 'file': apu_config.file.decode("utf-8")}

            apu_request = f'http://{apu.ip}:{apu.port}/autoStart'
            try:
                response = requests.post(url=apu_request, json=json_req, timeout=2)
                if response.status_code != status.HTTP_200_OK:
                    experience.status = ExperienceStatus.FAILED
                    experience.update()
                    raise FailedExperienceException(f'anwser from {apu.id}: {apu.name} - {apu.ip}:{apu.port}. {response.status_code}')
            except requests.exceptions.ConnectTimeout:
                experience.status = ExperienceStatus.FAILED
                experience.update()
                raise FailedExperienceException(f'Connect Timeout {apu.id}: {apu.name} - {apu.ip}:{apu.port}')

        experience.status = ExperienceStatus.RUNNING
        experience.update()


def finish_experience(id, app, db):
    with app.app_context():
        config_query = db.session.query(APU_Config, APU) \
            .filter(APU_Config.experience == id) \
            .filter(APU_Config.apu == APU.id).all()
        experience = db.session.query(Experience).get(id)
        if not experience:
            raise NoResultFound

        experience.status = ExperienceStatus.FINISHED
        experience.update()

        # if no apu config, those lines wont be executed

        request_response = []
        for apu_config, apu in config_query:
            apu_request = f'http://{apu.ip}:{apu.port}/autoStop'
            try:
                response = requests.get(url=apu_request, timeout=2)
                request_response.append(f'{apu.name}: {response.status_code}')
            except requests.exceptions.ConnectTimeout:
                request_response.append(f'{apu.name}: ConnectTimeout')
    return request_response

