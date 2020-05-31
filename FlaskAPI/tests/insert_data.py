from _datetime import datetime, timedelta

from models import Profile, Experience, APU, APU_Config, Role, ExperienceStatus


def insert_db_info():
    role = Role(role_name='test_role')
    role.add(role)

    profile = Profile(name='TEST_USER', email='jean18.jh@gmail.com', role=1, picture=None, num_test=0,
                      register_date=datetime.now())
    profile.add(profile)

    apu = APU(ip='127.0.0.1', port=5001, name='APU_TEST')
    apu.add(apu)

    apu = APU(ip='127.0.0.1', port=5002, name='APU_TEST2')
    apu.add(apu)

    experience = Experience(name='Testing Experience    ', profile=1, register_date=datetime.now(),
                            begin_date=datetime.now() + timedelta(0, 20),
                            end_date=datetime.now() + timedelta(0, 30), status=ExperienceStatus.SCHEDULED)

    experience.add(experience)
    #experience = Experience(name='TEST_EXPERIENCE', profile=1, register_date=datetime.now(),
#                            begin_date=datetime.now() + timedelta(0, 5),
#                            end_date=datetime.now() + timedelta(0, 10), status=ExperienceStatus.SCHEDULED)
    #experience.add(experience)


    apu_config = APU_Config(experience=1, apu=1, file=str.encode('THIS IS A RANDOM TEST FILE'))
    #apu_config.add(apu_config)
    #apu_config = APU_Config(experience=2, apu=1, file=str.encode('THIS IS A RANDOM TEST FILE2'))
    #apu_config.add(apu_config)
    #apu_config = APU_Config(experience=2, apu=2, file=str.encode('THIS IS A RANDOM TEST FILE3'))
    #apu_config.add(apu_config)




