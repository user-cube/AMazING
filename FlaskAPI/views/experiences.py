from flask_jwt_extended import jwt_required, get_raw_jwt
from _datetime import datetime, timedelta

from flask import request, jsonify, Blueprint
from flask_restful import reqparse
from flask_api import status
from sqlalchemy import or_, and_

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError
from sqlalchemy.orm.exc import NoResultFound

from models import db, Experience, Profile, APU_Config, ExperienceStatus
from views.base import get_user_by_email, UnauthorizedException, ExperienceScheduleException

from schedule.experience_schedule import experience_scheduler_manager


experiences_blueprint = Blueprint('experiences', __name__, )

parser = reqparse.RequestParser()
parser.add_argument('content')
parser.add_argument('userID')
parser.add_argument('date')
parser.add_argument('begin_date')
parser.add_argument('end_date')
parser.add_argument('status')


def format_experience_calendar(experince_calendar_fragment):
    experience = experince_calendar_fragment[0].serializable
    profile = experince_calendar_fragment[1].serializable
    experience['author'] = profile['name']
    experience['email'] = profile['email']
    return experience


def return_experince_in_range_datetime(begin_date, end_date):
    experience_query = db.session.query(Experience).filter(
        or_(
            and_((begin_date <= Experience.begin_date), (Experience.begin_date <= end_date)),
            and_((begin_date <= Experience.end_date), (Experience.end_date <= end_date))
        )
    ).all()
    return experience_query


@experiences_blueprint.route('/experience', methods=['GET'], strict_slashes=False)
@jwt_required
def list_experience():
    parse_data = parser.parse_args()
    experiences_query = db.session.query(Experience, Profile).filter(Experience.profile == Profile.id)
    # Apply filters
    if parse_data['userID']:
        experiences_query = experiences_query.filter(Experience.profile == parse_data['userID'])

    if parse_data['date']:
        date_start = datetime.strptime(parse_data['date'], "%Y-%m-%d").date()
        date_finish = date_start + timedelta(days=1)
        experiences_query = experiences_query.filter(Experience.begin_date >= date_start).filter(
            date_finish >= Experience.end_date)

    else:
        if parse_data['begin_date']:
            date = datetime.strptime(parse_data['begin_date'], "%Y-%m-%d").date()
            experiences_query = experiences_query.filter(Experience.begin_date >= date)
        if parse_data['end_date']:
            date = datetime.strptime(parse_data['end_date'], "%Y-%m-%d").date()
            experiences_query = experiences_query.filter(Experience.end_date <= date)
    if parse_data['status']:
        experiences_query = experiences_query.filter(Experience.status == parse_data['status'])
    if parse_data['content']:
        experiences_query = experiences_query.filter(Experience.name.contains(parse_data['content']))
    q = experiences_query.order_by(Experience.begin_date.asc()).all()
    response = []
    for experience, profile in q:
        experience = experience.serializable
        profile = profile.serializable
        experience['author'] = profile['name']
        response.append(experience)
    return jsonify(response)


@experiences_blueprint.route('/experience', methods=['POST'], strict_slashes=False)
@jwt_required
def insert_experience():
    jwt_data = get_raw_jwt()
    email = jwt_data['email']
    profile = get_user_by_email(email)
    raw_data = request.get_json(force=True)
    try:
        begin_date = datetime.strptime(raw_data['begin_date'], "%Y-%m-%d %H:%M:%S")
        end_date = datetime.strptime(raw_data['end_date'], "%Y-%m-%d %H:%M:%S")
        scheduled_experience = return_experince_in_range_datetime(begin_date, end_date)
        if len(scheduled_experience) > 0:
            raise ExperienceScheduleException(scheduled_experience)

        experience = Experience(name=raw_data['name'],
                                begin_date=begin_date,
                                end_date=end_date,
                                status=ExperienceStatus.SCHEDULED,
                                profile=profile.id,
                                register_date=datetime.now())

        config_node_list = []

        experience.add(experience)
        if 'config_node' in raw_data.keys():
            for apu_config in raw_data['config_node']:
                if apu_config['file']:
                    new_apu_config = APU_Config(apu=apu_config['apu'],
                                                experience=experience.id,
                                                file=str.encode(apu_config['file']))
                    new_apu_config.add(new_apu_config)
                    config_node_list.append(new_apu_config.serializable)

        profile.num_test += 1
        profile.update()
        results = jsonify({'experience': experience.serializable, 'config_node': config_node_list})
        results.status_code = status.HTTP_201_CREATED
        experience_scheduler_manager.manage_next_experience(experience.id)

    except ValidationError as err:
        results = jsonify({"ERROR": err.__str__()})
        results.status_code = status.HTTP_403_FORBIDDEN
    except SQLAlchemyError as err:
        db.session.rollback()
        results = jsonify({"ERROR": err.__str__()})
        results.status_code = status.HTTP_400_BAD_REQUEST
    except KeyError as err:
        db.session.rollback()
        results = jsonify({"ERROR": f" Missing key {err}"})
        results.status_code = status.HTTP_400_BAD_REQUEST
    except ExperienceScheduleException as err:
        experiences = [ex.serializable for ex in err.messages]
        results = jsonify({'ERROR': 'There are experiences scheduled in the requested range time',
                           'experiences': experiences})
        results.status_code = status.HTTP_400_BAD_REQUEST
    return results


@experiences_blueprint.route('/experience/<int:id>', methods=['GET'], strict_slashes=False)
@jwt_required
def info_experience(id):
    try:
        experience_query = db.session.query(Experience, Profile.name) \
            .filter(Experience.id == id) \
            .filter(Experience.profile == Profile.id).one()

        apu_config_query = db.session.query(APU_Config) \
            .filter(APU_Config.experience == id).all()
        if not experience_query:
            raise NoResultFound(id)

        response = {'experience': experience_query[0].serializable,
                    'author': experience_query[1],
                    'config_list': [apu_config.serializable for apu_config in apu_config_query]}
        results = jsonify(response)
        results.status_code = status.HTTP_200_OK

    except NoResultFound:
        results = jsonify({"Error": f"No item found for id {id}"})
        results.status_code = status.HTTP_404_NOT_FOUND

    except Exception as err:
        results = jsonify({"Error": err.__str__()})
        results.status_code = status.HTTP_400_BAD_REQUEST

    return results


@experiences_blueprint.route('/experience/<int:id>', methods=['PUT'], strict_slashes=False)
@jwt_required
def put(id):
    jwt_data = get_raw_jwt()
    email = jwt_data['email']
    user_id = get_user_by_email(email).id
    raw_data = request.get_json(force=True)
    experience = db.session.query(Experience).get(id)

    try:
        if not experience:
            raise NoResultFound
        if experience.profile != user_id and not jwt_data['isAdmin']:
            raise UnauthorizedException()
        begin_date = datetime.strptime(raw_data['begin_date'], "%Y-%m-%d %H:%M:%S")
        end_date = raw_data['end_date']

        scheduled_experience = return_experince_in_range_datetime(begin_date, end_date)
        if not len(scheduled_experience) == 0 \
                or (len(scheduled_experience) == 1 and scheduled_experience[0].id == experience.id):
            raise ExperienceScheduleException(scheduled_experience)
        experience.name = raw_data['name']
        experience.begin_date = begin_date
        experience.end_date = end_date
        experience.register_date = datetime.now()

        experience.update()
        results = jsonify(experience.serializable)
        results.status_code = status.HTTP_200_OK
        experience_scheduler_manager.manage_next_experience()

    except ValidationError as err:
        results = jsonify({"ERROR": err.messages})
        results.status_code = status.HTTP_403_FORBIDDEN
    except SQLAlchemyError as e:
        db.session.rollback()
        results = jsonify({"ERROR": str(e)})
        results.status_code = status.HTTP_400_BAD_REQUEST
    except KeyError as err:
        db.session.rollback()
        results = jsonify({"ERROR": f" Missing key {err}"})
        results.status_code = status.HTTP_400_BAD_REQUEST
    except UnauthorizedException:
        db.session.rollback()
        results = jsonify({"ERROR": f'Unauthorized Access for: Experience.id: {id}'})
        results.status_code = status.HTTP_401_UNAUTHORIZED
    except ExperienceScheduleException as err:
        experiences = [ex.serializable for ex in err.messages]
        results = jsonify({'ERROR': 'There are experiences scheduled in the requested range time',
                           'experiences': experiences})
        results.status_code = status.HTTP_400_BAD_REQUEST
    except NoResultFound:
        db.session.rollback()
        results = jsonify({"ERROR": f'Item not found experience id: {id}'})
        results.status_code = status.HTTP_404_NOT_FOUND
    return results


@experiences_blueprint.route('/experience/<int:id>', methods=['DELETE'], strict_slashes=False)
@jwt_required
def delete_experience(id):
    jwt_data = get_raw_jwt()
    email = jwt_data['email']
    user_id = get_user_by_email(email).id
    experience = db.session.query(Experience).get(id)

    try:
        if not experience:
            raise NoResultFound(f"Experience not founded, id: {id}")
        if experience.profile != user_id and not jwt_data['isAdmin']:
            raise UnauthorizedException()
        profile = db.session.query(Profile).get(experience.profile)
        experience.delete(experience)
        profile.num_test -= 1
        profile.update()
        results = jsonify(experience.serializable)
        results.status_code = status.HTTP_200_OK

        experience_scheduler_manager.remove_schedule_experience(experience.id)

    except ValidationError as err:
        results = jsonify({"ERROR": err.messages})
        results.status_code = status.HTTP_403_FORBIDDEN
    except SQLAlchemyError as e:
        db.session.rollback()
        results = jsonify({"ERROR": str(e)})
        results.status_code = status.HTTP_400_BAD_REQUEST
    except UnauthorizedException:
        db.session.rollback()
        results = jsonify({"ERROR": f'Unauthorized Access for: Experience.id: {id}'})
        results.status_code = status.HTTP_401_UNAUTHORIZED
    except NoResultFound:
        db.session.rollback()
        results = jsonify({"ERROR": f'Item not found experience id: {id}'})
        results.status_code = status.HTTP_404_NOT_FOUND
    return results


@experiences_blueprint.route('/experience/now', methods=['GET'], strict_slashes=False)
def experience_calendar():
    date_now = datetime.now()
    experience_schedule_query = db.session.query(Experience, Profile) \
        .filter(Experience.end_date >= date_now) \
        .filter(Experience.profile == Profile.id) \
        .order_by(Experience.begin_date.asc()) \
        .limit(2) \
        .all()
    calendar = {'current_experience': None, 'next_experience': None}

    if len(experience_schedule_query) == 2:
        if datetime.strptime(experience_schedule_query[0][0].serializable['begin_date'],
                             "%Y-%m-%d %H:%M:%S") < date_now:
            calendar['current_experience'] = format_experience_calendar(experience_schedule_query[0])
            calendar['next_experience'] = format_experience_calendar(experience_schedule_query[1])
        else:
            calendar['next_experience'] = format_experience_calendar(experience_schedule_query[0])

    elif len(experience_schedule_query) == 1:
        if datetime.strptime(experience_schedule_query[0][0].serializable['begin_date'],
                             "%Y-%m-%d %H:%M:%S") < date_now:
            calendar['current_experience'] = format_experience_calendar(experience_schedule_query[0])
        else:
            calendar['next_experience'] = format_experience_calendar(experience_schedule_query[0])
    return calendar


@experiences_blueprint.route('/experience/<int:experience_id>/node', methods=['POST'], strict_slashes=False)
@jwt_required
def insert_apu_config(experience_id):
    jwt_data = get_raw_jwt()
    email = jwt_data['email']
    profile = get_user_by_email(email)
    raw_data = request.get_json(force=True)
    experience = db.session.query(Experience).get(experience_id)
    try:
        if experience.profile != profile.id and not jwt_data['isAdmin']:
            raise UnauthorizedException
        apu_config = APU_Config(apu=raw_data['apu'], file=str.encode(raw_data['file']), experience=experience.id)
        apu_config.add(apu_config)
        results = jsonify(apu_config.serializable)

    except ValidationError as err:
        results = jsonify({"ERROR": err.messages})
        results.status_code = status.HTTP_403_FORBIDDEN
    except SQLAlchemyError as e:
        db.session.rollback()
        results = jsonify({"ERROR": str(e)})
        results.status_code = status.HTTP_400_BAD_REQUEST
    except KeyError as err:
        db.session.rollback()
        results = jsonify({"ERROR": f" Missing key {err}"})
        results.status_code = status.HTTP_400_BAD_REQUEST
    except UnauthorizedException:
        results = jsonify({'Error': f'Unauthorized access to selected content, Experience {id}'})
        results.status_code = status.HTTP_401_UNAUTHORIZED

    return results


@experiences_blueprint.route('/experience/<int:experience_id>/node/<apu_config_id>', methods=['GET'], strict_slashes=False)
@jwt_required
def get_apu_config(experience_id, apu_config_id):
    jwt_data = get_raw_jwt()
    email = jwt_data['email']
    profile = get_user_by_email(email)
    experience, apu_config = db.session.query(Experience, APU_Config) \
        .filter(APU_Config.id == apu_config_id). \
        filter(Experience.id == experience_id).one()
    try:
        if experience.profile != profile.id and not jwt_data['isAdmin']:
            raise UnauthorizedException
        if not experience or not apu_config:
            raise NoResultFound
        results = jsonify(apu_config.serializable)
    except UnauthorizedException:
        results = jsonify({'Error': f'Unauthorized access to selected content, Apu_Config {apu_config_id}'})
        results.status_code = status.HTTP_401_UNAUTHORIZED
    except NoResultFound:
        results = jsonify({"Error": f"No item found for Experience{experience_id} or Apu_Config {apu_config_id}"})
        results.status_code = status.HTTP_404_NOT_FOUND

    return results


@experiences_blueprint.route('/experience/<int:experience_id>/node/<apu_config_id>', methods=['PUT'], strict_slashes=False)
@jwt_required
def alter_apu_config(experience_id, apu_config_id):
    jwt_data = get_raw_jwt()
    email = jwt_data['email']
    profile = get_user_by_email(email)
    raw_data = request.get_json(force=True)
    experience, apu_config = db.session.query(Experience, APU_Config) \
        .filter(APU_Config.id == apu_config_id). \
        filter(Experience.id == experience_id).one()
    try:
        if experience.profile != profile.id and not jwt_data['isAdmin']:
            raise UnauthorizedException
        if not experience or not apu_config:
            raise NoResultFound
        apu_config.apu = raw_data['apu']
        apu_config.file = str.encode(raw_data['file'])
        apu_config.update()
        results = jsonify(apu_config.serializable)

    except ValidationError as err:
        results = jsonify({"ERROR": err.messages})
        results.status_code = status.HTTP_403_FORBIDDEN
    except SQLAlchemyError as e:
        db.session.rollback()
        results = jsonify({"ERROR": str(e)})
        results.status_code = status.HTTP_400_BAD_REQUEST
    except KeyError as err:
        db.session.rollback()
        results = jsonify({"ERROR": f" Missing key {err}"})
        results.status_code = status.HTTP_400_BAD_REQUEST
    except UnauthorizedException:
        results = jsonify({'Error': f'Unauthorized access to selected content, Apu_Config {apu_config_id}'})
        results.status_code = status.HTTP_401_UNAUTHORIZED
    except NoResultFound:
        results = jsonify({"Error": f"No item found for Experience{experience_id} or Apu_Config {apu_config_id}"})
        results.status_code = status.HTTP_404_NOT_FOUND

    return results


@experiences_blueprint.route('/experience/<int:experience_id>/node/<apu_config_id>', methods=['DELETE'], strict_slashes=False)
@jwt_required
def delete_apu_config(experience_id, apu_config_id):
    jwt_data = get_raw_jwt()
    email = jwt_data['email']
    profile = get_user_by_email(email)
    experience, apu_config = db.session.query(Experience, APU_Config) \
        .filter(APU_Config.id == apu_config_id). \
        filter(Experience.id == experience_id).one()
    try:
        if experience.profile != profile.id and not jwt_data['isAdmin']:
            raise UnauthorizedException
        if not experience or not apu_config:
            raise NoResultFound

        apu_config.delete(apu_config)
        results = jsonify(apu_config.serializable)

    except ValidationError as err:
        results = jsonify({"ERROR": err.messages})
        results.status_code = status.HTTP_403_FORBIDDEN
    except SQLAlchemyError as e:
        db.session.rollback()
        results = jsonify({"ERROR": str(e)})
        results.status_code = status.HTTP_400_BAD_REQUEST
    except KeyError as err:
        db.session.rollback()
        results = jsonify({"ERROR": f" Missing key {err}"})
        results.status_code = status.HTTP_400_BAD_REQUEST
    except UnauthorizedException:
        results = jsonify({'Error': f'Unauthorized access to selected content, Apu_Config {apu_config_id}'})
        results.status_code = status.HTTP_401_UNAUTHORIZED
    except NoResultFound:
        results = jsonify({"Error": f"No item found for Experience{experience_id} or Apu_Config {apu_config_id}"})
        results.status_code = status.HTTP_404_NOT_FOUND

    return results
