from _datetime import datetime, timedelta

from flask_sqlalchemy import SQLAlchemy

from models import Profile, Experience, APU, APU_Config, Role, ExperienceStatus


def insert_db_info(db: SQLAlchemy):
    role = Role(role_name='test_role')
    profile = Profile(name='TEST_USER', email='test_email@test.com', role=1, picture=None, num_test=0,
                      register_date=datetime.now())
    apu = APU(ip='127.0.0.1', port=5001, name='APU_TEST')
    experience = Experience(name='TEST_EXPERIENCE', profile=1, register_date=datetime.now(), begin_date=datetime.now(),
                            end_date=datetime.now() + timedelta(10), status=ExperienceStatus.SCHEDULED)
    apu_config = APU_Config(experience=1, apu=1, file=str.encode('THIS IS A RANDOM TEST FILE'))

    role.add(role)
    profile.add(profile)
    apu.add(apu)
    experience.add(experience)
    apu_config.add(apu_config)
