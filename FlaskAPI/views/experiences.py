from flask_jwt_extended import jwt_required, get_raw_jwt
from _datetime import datetime, timedelta

from flask import request, jsonify, make_response
from flask_restful import Resource, reqparse
from flask_api import status

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from models import db, Experience, Profile, Template
from views.base import get_user_by_email

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
        q = experiences_query.all()
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
