import requests
from flask_api import status

from models import db, Experience, APU_Config, APU
from views.base import FailedExperienceException, ExperienceStatus

from sqlalchemy.orm.exc import NoResultFound


def start_experience(id):
    config_query = db.session.query(APU_Config, APU) \
        .filter(APU_Config.experience == id) \
        .filter(APU_Config.apu == APU.id).all()
    experience = db.session.query(Experience).get(id)
    if not experience:
        raise NoResultFound

        # if no apu config, those lines wont be executed
    for apu_config, apu in config_query:

        json_req = {'experience': id, 'file': apu_config.file.decode("utf-8")}

        #apu_request = f'http://{apu.ip}/autoStart'
        apu_request = f'http://{apu.ip}:5000/autoStart'
        response = requests.post(url=apu_request, json=json_req, timeout=2)
        if response.status_code != status.HTTP_200_OK:
            experience.status = ExperienceStatus.FAILED
            db.session.commit()
            raise FailedExperienceException

    experience.status = ExperienceStatus.RUNNING
    db.session.commit()


def finish_experience(id):
    config_query = db.session.query(APU_Config, APU) \
        .filter(APU_Config.experience == id) \
        .filter(APU_Config.apu == APU.id).all()
    experience = db.session.query(Experience).get(id)
    if experience:
        raise NoResultFound

    experience.status = ExperienceStatus.FINISHED
    db.session.commit()

    # if no apu config, those lines wont be executed

    for apu_config, apu in config_query:
        apu_request = f'http://{apu.ip}:5000/autoStop'
        response = requests.get(url=apu_request, timeout=2)
        if response.status_code != status.HTTP_200_OK:
            raise FailedExperienceException
