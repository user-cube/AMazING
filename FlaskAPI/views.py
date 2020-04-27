from flask_jwt_extended import jwt_required, get_raw_jwt, get_jti
from _datetime import datetime, timedelta

from models import *
from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource, reqparse
from flask_api import status

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

# Config Files
schema_blueprint = Blueprint('amazing', __name__)
api = Api(schema_blueprint)


#       Parse definition
parser = reqparse.RequestParser()
# users
parser.add_argument('typeID')
parser.add_argument('email')

# Users and Experience
parser.add_argument('content')

# Experience
parser.add_argument('userID')
parser.add_argument('date')
parser.add_argument('begin_date')
parser.add_argument('end_date')
parser.add_argument('status')


#       BASE Functions

def get_user_by_email(email):
    users_query = db.session().query(Profile).filter(Profile.email == email).one()
    return users_query.serializable



class RoleView(Resource):
    def get(self):
        role_query = db.session.query(Role).all()
        results = jsonify([role.serializable for role in role_query])
        return results


class UserView(Resource):
    @jwt_required
    def get(self):
        parse_data = parser.parse_args()
        jwt_data = get_raw_jwt()
        if not jwt_data['isAdmin']:
            results = jsonify()
            results.status_code = status.HTTP_401_UNAUTHORIZED
            return results

        users_query = db.session().query(Profile)

        if parse_data['typeID']:
            users_query = users_query.filter(Profile.role == parse_data['typeID'])
        if parse_data['email']:
            users_query = users_query.filter(Profile.email.contains(parse_data['email']))
        if parse_data['content']:
            users_query = users_query.filter(Profile.name.contains(parse_data['content']))
        q = users_query.all()
        return jsonify([result.serializable for result in q])

    @jwt_required
    def post(self):
        if not get_raw_jwt()['isAdmin']:
            results = jsonify()
            results.status_code = status.HTTP_401_UNAUTHORIZED
            return results
        raw_data = request.get_json(force=True)
        try:
            message = raw_data
            profile = Profile(name=message['name'], email=message['email'], role=message['role'], num_test=0,
                              register_date=datetime.now())
            profile.add(profile)
            return profile.serializable, status.HTTP_201_CREATED

        except ValidationError as err:
            resp = jsonify({"error": err.messages})
            resp.status_code = status.HTTP_403_FORBIDDEN
            return resp

        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp


class UserInfoView(Resource):
    @jwt_required
    def get(self, id):
        if not get_raw_jwt()['isAdmin']:
            results = jsonify()
            results.status_code = status.HTTP_401_UNAUTHORIZED
            return results
        user_query = db.session.query(Profile).get(id)
        user = jsonify(user_query.serializable)
        return user

    @jwt_required
    def put(self, id):
        jwt_data = get_raw_jwt()
        if not jwt_data['isAdmin']:
            results = jsonify()
            results.status_code = status.HTTP_401_UNAUTHORIZED
            return results

        raw_data = request.get_json(force=True)
        message = raw_data['role']
        profile = db.session.query(Profile).get(id)

        profile.role = message
        db.session.commit()
        return profile.serializable

"""
    @jwt_required
    def delete(self, id):
        email = get_raw_jwt()['jti']
        user_id = get_email_by_id(email)['id']

        if not user_id:
            resp = jsonify({"error": 'Non-existent user'})
            resp.status_code = 403
            return resp

        user = Profile.query.get_or_404(user_id)
        try:
            delete = user.delete(user)
            response = make_response()
            response.status_code = 204
            return response

        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_401_UNAUTHORIZED
            return resp

"""


class ProfileView(Resource):
    @jwt_required
    def get(self):
        email = get_raw_jwt()['email']
        users_query = db.session.query(Profile).filter(Profile.email==email).one()
        results = users_query.serializable
        return jsonify(results)

    @jwt_required
    def put(self):
        email = get_raw_jwt()['email']
        user = users_query = db.session().query(Profile).filter(Profile.email == email).one()
        raw_data = request.get_json(force=True)

        if raw_data['pic']:
            user.picture = raw_data['pic']
        user.name = raw_data['name']
        db.session.commit()
        return user.serializable


class ExperienceView(Resource):
    @jwt_required
    def get(self):
        parse_data = parser.parse_args()
        jwt_data = get_raw_jwt()
        experiences_query = db.session.query(Experience, Profile)
        # Apply filters
        if jwt_data['isAdmin']:
            if parse_data['userID']:
                experiences_query = experiences_query.filter(Experience.profile == parse_data['userID'])
        else:
            email = parse_data['email']
            user_id = get_user_by_email(email)['id']
            experiences_query = experiences_query.filter(Experience.profile == user_id)

        if parse_data['date']:
            date = datetime.strptime(parse_data['date'], "%Y-%m-%d %H:%M:%H").date()
            experiences_query = experiences_query.filter(Experience.begin_date >= date >= Experience.end_date)
        else:
            if parse_data['begin_date']:
                date = datetime.strptime(parse_data['begin_date'], "%Y-%m-%d %H:%M:%H").date()
                experiences_query = experiences_query.filter(Experience.begin_date >= date)
            if parse_data['end_date']:
                date = datetime.strptime(parse_data['end_date'], "%Y-%m-%d %H:%M:%H").date()
                experiences_query = experiences_query.filter(Experience.end_date <= date)
        if parse_data['status']:
            experiences_query = experiences_query.filter(Experience.status == parse_data['status'])
        if parse_data['content']:
            experiences_query = experiences_query.filter(Experience.name.contains(parse_data['content']))
        q = experiences_query.join(Profile).filter(Experience.profile == Profile.id).all()
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
        user_id = get_user_by_email(email)['id']
        raw_data = request.get_json(force=True)
        try:
            message = raw_data
            begin_date = datetime.strptime(message['begin_date'], "%Y-%m-%d %H:%M:%S")
            template = db.session.query(Template).get(message['template'])
            total_duration = message['num_test'] * (template.duration + 60)  # 1 min for test setup

            experience = Experience(name=message['name'],
                                    begin_date=begin_date,
                                    num_test=message['num_test'],
                                    end_date=begin_date + timedelta(0, total_duration),
                                    status='SCHEDULED',
                                    profile=user_id,
                                    template=message['template'],
                                    register_date=datetime.now())

            experience.add(experience)
            return experience.serializable, status.HTTP_201_CREATED

        except ValidationError as err:
            resp = jsonify({"error": err.messages})
            resp.status_code = status.HTTP_403_FORBIDDEN
            return resp

        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = status.HTTP_400_BAD_REQUEST
            return resp

class ExperienceInfoView(Resource):

    @jwt_required
    def get(self, id):
        jwt_data = get_raw_jwt()
        user_id = get_user_by_email(jwt_data['email'])['id']
        query = db.session.query(Experience, Template).filter(Experience.id==id).filter(Experience.template == Template.id).one()
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
        #date_now = datetime.strptime("2020-06-30", "%Y-%m-%d").date()
        print()
        experience_schedule_query = db.session.query(Experience, Profile) \
            .filter(Experience.end_date >= date_now) \
            .filter(Experience.profile == Profile.id) \
            .order_by(Experience.begin_date.asc()) \
            .limit(2) \
            .all()
        calendar = {'current_experience': None, 'next_experience': None}
        print(experience_schedule_query)
        print(len(experience_schedule_query))
        if len(experience_schedule_query) == 2:
            calendar['current_experience'] = self.format_experience_calendar(experience_schedule_query[0])
            calendar['next_experience'] = self.format_experience_calendar(experience_schedule_query[1])

        elif len(experience_schedule_query) == 1:
            if datetime.strptime(experience_schedule_query[0][0].serializable['begin_date'], "%Y-%m-%d %H:%M:%S").date() < date_now:
                calendar['current_experience'] = self.format_experience_calendar(experience_schedule_query[0])
            else:
                calendar['next_experience'] = self.format_experience_calendar(experience_schedule_query[0])
        return calendar

    @staticmethod
    def format_experience_calendar(experince_calendar_fragment):
        experience = experince_calendar_fragment[0].serializable
        profile = experince_calendar_fragment[1].serializable
        experience['author'] = profile['name']
        experience['email'] = profile['email']
        return experience


api.add_resource(UserView, '/user', '/user/')
api.add_resource(UserInfoView, '/user/<int:id>', '/user/<int:id>/')
api.add_resource(RoleView, '/role', '/role/')
api.add_resource(ProfileView, '/profile', '/profile/')
api.add_resource(ExperienceView, '/experience', '/experience/')
api.add_resource(ExperienceInfoView, '/experience/<int:id>', '/experience/<int:id>/')
api.add_resource(ExperienceScheduleView, '/experience/now', '/experience/now/')
