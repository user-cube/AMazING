from flask_jwt_extended import jwt_required, get_raw_jwt
from _datetime import datetime, timedelta

from flask import request, jsonify, make_response
from flask_restful import Resource, reqparse
from flask_api import status
from sqlalchemy import or_, and_

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from models import db, Experience, Profile, Template
from views.base import get_user_by_email, UnauthorizedException

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
            and_((begin_date <= Experience.begin_date),(Experience.begin_date <= end_date)),
            and_((begin_date <= Experience.end_date), (Experience.end_date <= end_date))
            )
    ).all()
    print("\n\n\n\n Queries", experience_query)
    return experience_query


class ExperienceView(Resource):
    @jwt_required
    def get(self):
        parse_data = parser.parse_args()
        jwt_data = get_raw_jwt()
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

    @jwt_required
    def post(self):
        jwt_data = get_raw_jwt()
        email = jwt_data['email']
        user_id = get_user_by_email(email).id
        raw_data = request.get_json(force=True)
        try:
            begin_date = datetime.strptime(raw_data['begin_date'], "%Y-%m-%d %H:%M:%S")
            template = db.session.query(Template).get(raw_data['template'])
            if 'end_date' in raw_data.keys():
                end_date = raw_data['end_date']
            else:
                total_duration = raw_data['num_test'] * (template.duration + 60)  # 1 min for test setup
                end_date = begin_date + timedelta(0, total_duration)
            scheduled_experience = return_experince_in_range_datetime(begin_date, end_date)
            if len(scheduled_experience) == 0:
                experience = Experience(name=raw_data['name'],
                                        begin_date=begin_date,
                                        num_test=raw_data['num_test'],
                                        end_date=end_date,
                                        status='SCHEDULED',
                                        profile=user_id,
                                        template=raw_data['template'],
                                        register_date=datetime.now())

                experience.add(experience)
                results = jsonify(experience.serializable)
                results.status_code = status.HTTP_201_CREATED
            else:
                experiences = [ex.serializable for ex in scheduled_experience]
                results = jsonify({'ERROR': 'There are experiences scheduled in the requested range time',
                                   'experiences': experiences})
                results.status_code = status.HTTP_400_BAD_REQUEST

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
        return results


class ExperienceInfoView(Resource):

    @jwt_required
    def get(self, id):
        jwt_data = get_raw_jwt()
        user_id = get_user_by_email(jwt_data['email']).id
        query = db.session.query(Experience, Template).filter(Experience.id == id).filter(
            Experience.template == Template.id).one()
        experience = query[0].serializable
        template = query[1].serializable
        if not jwt_data['isAdmin'] and experience.profile != user_id:
            results = jsonify()
            results.status_code = status.HTTP_401_UNAUTHORIZED
        results = make_response({"experience": experience, "template": template})
        results.status_code = status.HTTP_200_OK
        return results

    @jwt_required
    def put(self, id):
        jwt_data = get_raw_jwt()
        email = jwt_data['email']
        user_id = get_user_by_email(email).id
        raw_data = request.get_json(force=True)
        experience = db.session.query(Experience).get(id)

        try:
            if not experience:
                raise Exception(f"Experience not founded, id: {id}")
            if experience.profile != user_id and not jwt_data['isAdmin']:
                raise UnauthorizedException()
            begin_date = datetime.strptime(raw_data['begin_date'], "%Y-%m-%d %H:%M:%S")
            template = db.session.query(Template).get(raw_data['template'])
            if 'end_date' in raw_data.keys():
                end_date = raw_data['end_date']
            else:
                total_duration = raw_data['num_test'] * (template.duration + 60)  # 1 min for test setup
                end_date = begin_date + timedelta(0, total_duration)

            scheduled_experience = return_experince_in_range_datetime(begin_date, end_date)
            if len(scheduled_experience) == 0 \
                    or (len(scheduled_experience) == 1 and scheduled_experience[0].id == experience.id):

                experience.name = raw_data['name']
                experience.begin_date = begin_date
                experience.num_test = raw_data['num_test']
                experience.end_date = end_date
                experience.status = 'SCHEDULED'
                experience.template = raw_data['template']
                experience.register_date = datetime.now()

                db.session.commit()
                results = jsonify(experience.serializable)
                results.status_code = status.HTTP_200_OK
            else:
                experiences = [ex.serializable for ex in scheduled_experience]
                results = jsonify({'ERROR': 'There are experiences scheduled in the requested range time',
                                   'experiences': experiences})
                results.status_code = status.HTTP_400_BAD_REQUEST

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
        except UnauthorizedException as err:
            db.session.rollback()
            results = jsonify({"ERROR": f'Unauthorized Access for: Experience.id: {id}'})
            results.status_code = status.HTTP_401_UNAUTHORIZED
        except Exception as err:
            db.session.rollback()
            results = jsonify({"ERROR": err.__str__()})
            results.status_code = status.HTTP_404_NOT_FOUND
        return results


class ExperienceScheduleView(Resource):
    def get(self):
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
