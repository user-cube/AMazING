from functools import wraps
from flask_jwt_extended import jwt_required, get_raw_jwt, verify_jwt_in_request, get_jwt_claims
from _datetime import datetime, timedelta

from models import *
from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource, reqparse
from flask_api import status

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

import requests

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


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        jwt_data = get_raw_jwt()
        print(jwt_data)
        if not jwt_data['isAdmin']:
            results = jsonify({'ERROR': 'AUTHORIZATION_ERROR', 'CONTENT': 'Forbidden access, admins only!'})
            results.status_code = status.HTTP_403_FORBIDDEN
            return results
        else:
            return fn(*args, **kwargs)

    return wrapper


#       Class View

class RoleView(Resource):
    def get(self):
        role_query = db.session.query(Role).all()
        results = jsonify([role.serializable for role in role_query])
        return results


class UserView(Resource):
    @admin_required
    def get(self):

        parse_data = parser.parse_args()
        users_query = db.session().query(Profile)

        if parse_data['typeID']:
            users_query = users_query.filter(Profile.role == parse_data['typeID'])
        if parse_data['email']:
            users_query = users_query.filter(Profile.email.contains(parse_data['email']))
        if parse_data['content']:
            users_query = users_query.filter(Profile.name.contains(parse_data['content']))
        q = users_query.all()
        return jsonify([result.serializable for result in q])

    @admin_required
    def post(self):
        raw_data = request.get_json(force=True)
        try:
            profile = Profile(name=raw_data['name'], email=raw_data['email'], role=raw_data['role'], num_test=0,
                              register_date=datetime.now())
            profile.add(profile)
            results = profile.serializable
            results.status_code = status.HTTP_201_CREATED

        except ValidationError as err:
            results = jsonify({"error": err.messages})
            results.status_code = status.HTTP_403_FORBIDDEN

        except SQLAlchemyError as err:
            db.session.rollback()
            results = jsonify({"error": str(err)})
            results.status_code = status.HTTP_400_BAD_REQUEST

        except KeyError as err:
            results = jsonify({"ERROR": f" Missing key {err}"})
            results.status_code = status.HTTP_400_BAD_REQUEST
        return results


class UserInfoView(Resource):
    @admin_required
    def get(self, id):
        user_query = db.session.query(Profile).get(id)
        user = jsonify(user_query.serializable)
        return user

    @admin_required
    def put(self, id):
        raw_data = request.get_json(force=True)
        try:
            message = raw_data['role']
            profile = db.session.query(Profile).get(id)

            profile.role = message
            db.session.commit()
            results = jsonify(profile.serializable)
            results.status_code = status.HTTP_202_ACCEPTED
        except KeyError as err:
            results = jsonify({"ERROR": f" Missing key {err}"})
            results.status_code = status.HTTP_400_BAD_REQUEST
        return results

    """
    @jwt_required
    def delete(self, id):
        email = get_raw_jwt()['jti']
        user_id = get_email_by_id(email)['id']

        if not user_id:
            results = jsonify({"error": 'Non-existent user'})
            results.status_code = 403
            return results

        user = Profile.query.get_or_404(user_id)
        try:
            delete = user.delete(user)
            response = make_response()
            response.status_code = 204
            return resultsonse

        except SQLAlchemyError as e:
            db.session.rollback()
            results = jsonify({"error": str(e)})
            results.status_code = status.HTTP_401_UNAUTHORIZED
            return results

"""


class ProfileView(Resource):
    @jwt_required
    def get(self):
        jwt_raw = get_raw_jwt()
        email = jwt_raw['email']
        try:
            profile = db.session.query(Profile).filter(Profile.email == email).one()
            results = jsonify(profile.serializable)
        except SQLAlchemyError:
            results = jsonify({"ERROR": f"User email not registered, email: {email}"})
            results.status_code = status.HTTP_204_NO_CONTENT
        return results

    @jwt_required
    def put(self):
        email = get_raw_jwt()['email']
        user = db.session().query(Profile).filter(Profile.email == email).one()
        raw_data = request.get_json(force=True)
        try:
            if raw_data['pic']:
                user.picture = raw_data['pic']
            user.name = raw_data['name']
            db.session.commit()
            results = jsonify(user.serializable)
            results.status_code = status.HTTP_202_ACCEPTED
        except KeyError as err:
            results = jsonify({"ERROR": f" Missing key {err}"})
            results.status_code = status.HTTP_400_BAD_REQUEST
        return results


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
            results = jsonify({"ERROR": err.messages})
            results.status_code = status.HTTP_403_FORBIDDEN
            return results

        except SQLAlchemyError as e:
            db.session.rollback()
            results = jsonify({"ERROR": str(e)})
            results.status_code = status.HTTP_400_BAD_REQUEST
            return results


class ExperienceInfoView(Resource):

    @jwt_required
    def get(self, id):
        jwt_data = get_raw_jwt()
        user_id = get_user_by_email(jwt_data['email'])['id']
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
                calendar['current_experience'] = self.format_experience_calendar(experience_schedule_query[0])
                calendar['next_experience'] = self.format_experience_calendar(experience_schedule_query[1])
            else:
                calendar['next_experience'] = self.format_experience_calendar(experience_schedule_query[0])

        elif len(experience_schedule_query) == 1:
            if datetime.strptime(experience_schedule_query[0][0].serializable['begin_date'],
                                 "%Y-%m-%d %H:%M:%S") < date_now:
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


class TemplateView(Resource):
    @jwt_required
    def get(self):
        parse_data = parser.parse_args()
        return jsonify(self.template_query(parse_data))

    @jwt_required
    def post(self):
        raw_data = request.get_json(force=True)

    @staticmethod
    def template_query(parse_data, id=None):
        templates_query = db.session.query(Template, Profile, APU_Config) \
            .filter(Template.profile == Profile.id) \
            .filter(Template.id == APU_Config.template)
        # Apply filters

        if id:
            templates_query = templates_query.filter(Template.id == id)
        else:
            if parse_data['userID']:
                templates_query = templates_query.filter(Template.profile == parse_data['userID'])
            if parse_data['content']:
                templates_query = templates_query.filter(Template.name.contains(parse_data['content']))
        query_results = templates_query.all()

        response = {}
        for template, profile, apu_config in query_results:
            if not template in response.keys():
                response[template] = {'author': profile, 'config': []}
            response[template]['config'].append(apu_config.serializable)
        results = []
        for template in response.keys():
            results.append({'template': template.serializable, 'author': response[template]['author'].name,
                            'config_list': response[template]['config']})
        return results

class TemplateInfoView(Resource):
    def get(self, id):
        parse_data = parser.parse_args()
        results = TemplateView.template_query(parse_data, id)
        return jsonify(results[0])


class NodeView(Resource):
    @jwt_required
    def get(self):
        apu_query = db.session.query(APU).all()
        return jsonify([apu.serializable for apu in apu_query])

    @admin_required
    def post(self):
        raw_data = request.get_json(force=True)
        db.session.query(APU)
        try:
            apu = APU(ip=raw_data['ip'], name=raw_data['name'])
            apu.add(apu)
            return apu.serializable, status.HTTP_201_CREATED

        except ValidationError as err:
            results = jsonify({"ERROR": err.messages})
            results.status_code = status.HTTP_403_FORBIDDEN
            return results

        except SQLAlchemyError as e:
            db.session.rollback()
            results = jsonify({"ERROR": str(e)})
            results.status_code = status.HTTP_400_BAD_REQUEST
            return results


class NodeInfoView(Resource):

    @jwt_required
    def get(self, id):
        apu = db.session.query(APU).get(id)
        if not apu:
            results = jsonify({"ERROR": f"APU not found, id {id}"})
            results.status_code = status.HTTP_404_NOT_FOUND
            return results

        apu_request = f'http://{apu.ip}:5000/testi'
        try:
            results = requests.get(apu_request, timeout=2)
            return jsonify(results.json())
        except requests.exceptions.ConnectionError:
            results = jsonify({"ERROR": f"{apu.name}: not founded"})
            results.status_code = status.HTTP_444_CONNECTION_CLOSED_WITHOUT_RESPONSE
            return results

    @admin_required
    def put(self, id):
        raw_data = request.get_json(force=True)
        apu = db.session.query(APU).get(id)
        print("\n\n id", apu)
        if not apu:
            results = jsonify({"ERROR": f" Apu {id} not registered"})
            results.status_code = status.HTTP_204_NO_CONTENT
            return results
        try:
            if raw_data['name']:
                apu.name = raw_data['name']
            if raw_data['ip']:
                apu.ip = raw_data['ip']
            db.session.commit()
            results = jsonify(apu.serializable)
            results.status_code = status.HTTP_202_ACCEPTED
        except SQLAlchemyError or KeyError as err:
            db.session.rollback()
            results = jsonify({"ERROR": str(err.messages)})
            results.status_code = status.HTTP_400_BAD_REQUEST
        except KeyError as err:
            results = jsonify({"ERROR": f" Missing key {err}"})
            results.status_code = status.HTTP_400_BAD_REQUEST
        return results

    @admin_required
    def delete(self, id):
        apu = db.session.query(APU).get(id)
        if not apu:
            results = jsonify({"ERROR": f"APU not found, id {id}"})
            results.status_code = status.HTTP_404_NOT_FOUND
            return results
        apu.delete(apu)
        return jsonify(apu.serializable)


api.add_resource(UserView, '/user', '/user/')
api.add_resource(UserInfoView, '/user/<int:id>', '/user/<int:id>/')
api.add_resource(RoleView, '/role', '/role/')
api.add_resource(ProfileView, '/profile', '/profile/')
api.add_resource(ExperienceView, '/experience', '/experience/')
api.add_resource(ExperienceInfoView, '/experience/<int:id>', '/experience/<int:id>/')
api.add_resource(ExperienceScheduleView, '/experience/now', '/experience/now/')
api.add_resource(TemplateView, '/template', '/template/')
api.add_resource(TemplateInfoView, '/template/<int:id>', '/template/<int:id>/')
api.add_resource(NodeView, '/node', '/node/')
api.add_resource(NodeInfoView, '/node/<int:id>', '/node/<int:id>/')
