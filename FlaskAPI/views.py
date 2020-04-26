from flask_jwt_extended import jwt_required, get_raw_jwt, get_jti
from _datetime import datetime, timedelta
from models import *
from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource, reqparse
from flask_api import status

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

# COnfig Files
schema_blueprint = Blueprint('amazing', __name__)
api = Api(schema_blueprint)

# Schema Config

role_schema = RoleSchema()
profile_schema = ProfileSchema()
template_schema = TemplateSchema()
experience_schema = ExperienceSchema()
apu_schema = APUSchema()
apuconfig_schema = APUConfigSchema()
apuconfig_template_schema = APUConfig_TemplateSchema()

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
    results = profile_schema.dump(users_query)
    if results:
        return results
    return


class RoleView(Resource):
    def get(self):
        role_query = db.session.query(Role).all()
        results = profile_schema.dump(role_query, many=True)
        return results


class UserView(Resource):
    @jwt_required
    def get(self, *filters):
        parse_data = parser.parse_args()
        raw_data = get_raw_jwt()
        print("RAW ", raw_data)
        if not raw_data['isAdmin']:
            results = jsonify()
            results.status_code = status.HTTP_401_UNAUTHORIZED
            return results
        users_query = db.session().query(Profile)

        if parse_data['typeID']:
            users_query = users_query.filter(Profile.role == parse_data['typeID'])
        if parse_data['email']:
            users_query = users_query.filter(Profile.email == parse_data['email'])
        if parse_data['content']:
            users_query = users_query.filter(Profile.name.contains(parse_data['content']))

        results = profile_schema.dump(users_query.all(), many=True)
        print("RESULTS ", results)
        return results

    @jwt_required
    def post(self):
        if not get_raw_jwt()['isAdmin']:
            results = jsonify()
            results.status_code = status.HTTP_401_UNAUTHORIZED
            return results
        raw_dict = request.get_json(force=True)
        try:
            message = raw_dict['message']
            profile = Profile(name=message['name'], email=message['email'], role=message['role'], num_testes=0,
                              register_date=datetime.datetime.now())
            profile.add(profile)
            results = profile_schema.dump(profile)
            return results, 201

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
        user_query = db.session.query(Profile).query.get_or_404(id)
        user = profile_schema.dump(user_query)
        return user

    @jwt_required
    def put(self, id):
        jwt_data = get_raw_jwt()
        if not jwt_data['isAdmin']:
            results = jsonify()
            results.status_code = status.HTTP_401_UNAUTHORIZED
            return results

        raw_dict = request.get_json(force=True)
        message = raw_dict['message']
        profile = db.session.query(Profile).get(id)

        profile.name = message['name']
        profile.email = email=message['email']
        profile.role = message['role']
        return profile

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
        users_query = db.session(Profile).query.filter_by(email=email)
        results = profile_schema.dump(users_query, many=True)
        return results

    def put(self):
        email = get_raw_jwt()['email']

        user = users_query = db.session().query(Profile).filter(Profile.email == email).one()
        message = request.get_json(force=True)['message']
        user.picture = message['picture']
        user.name = message['name']
        user.update(user)
        return profile_schema.dump(user)


class ExperienceView(Resource):
    @jwt_required
    def get(self):
        parse_data = parser.parse_args()
        raw_data = get_raw_jwt()
        experiences_query = db.session.query(Experience)
        # Apply filters
        if raw_data['isAdmin']:
            if parse_data['userID']:
                experiences_query = experiences_query.filter(Experience.profile == parse_data['userID'])
        else:
            email = parse_data['email']
            user_id = get_user_by_email(email)['id']
            experiences_query = experiences_query.filter(Experience.profile == user_id)

        if parse_data['date']:
            date = datetime.strptime(parse_data['date'], "%Y-%m-%d").date()
            experiences_query = experiences_query.filter(Experience.begin_date >= date >= Experience.end_date)
        else:
            if parse_data['begin_date']:
                date = datetime.strptime(parse_data['begin_date'], "%Y-%m-%d").date()
                experiences_query = experiences_query.filter(Experience.begin_date >= date)
            if parse_data['end_date']:
                date = datetime.strptime(parse_data['end_date'], "%Y-%m-%d").date()
                experiences_query = experiences_query.filter(Experience.end_date <= date)
        if parse_data['status']:
            experiences_query = experiences_query.filter(Experience.status == parse_data['status'])

        results = experience_schema.dump(experiences_query.all(), many=True)
        return results

    @jwt_required
    def post(self):
        raw_data = get_raw_jwt()
        email = raw_data['email']
        user_id = get_user_by_email(email)['id']
        raw_dict = request.get_json(force=True)
        try:
            message = raw_dict['message']
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

            return experience_schema.dump(experience), status.HTTP_201_CREATED

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
        claims = get_raw_jwt()
        user_id = get_user_by_email(claims['email'])
        query = db.session.query(Experience, Template).filter(Experience.id==id).filter(Experience.template == Template.id).one()
        experience = experience_schema.dump(query[0])
        template = template_schema.dump(query[1])
        if not claims['isAdmin'] and experience.profile != user_id:
            results = jsonify()
            results.status_code = status.HTTP_401_UNAUTHORIZED
        results = make_response({"experience": experience, "template": template})
        results.status_code = status.HTTP_200_OK
        return results

api.add_resource(UserView, '/user')
api.add_resource(UserInfoView, '/user/<int:id>')
api.add_resource(RoleView, '/role')
api.add_resource(ProfileView, '/profile')
api.add_resource(ExperienceView, '/experience')
api.add_resource(ExperienceInfoView, '/experience/<int:id>')
