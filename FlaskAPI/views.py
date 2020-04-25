from flask_jwt_extended import jwt_required, get_raw_jwt, get_jti

from models import *
from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

schema_blueprint = Blueprint('amazing', __name__)
api = Api(schema_blueprint)

role_schema = RoleSchema()
profile_schema = ProfileSchema()
template_schema = TemplateSchema()
experience_schema = ExperienceSchema()
apu_schema = APUSchema()
apuconfig_schema = APUConfigSchema()
apuconfig_template_schema = APUConfig_TemplateSchema()


def retrieve_id(email):
    # email = get_raw_jwt()['jti']
    users_query = Profile.query.filter_by(email=email)
    results = profile_schema.dump(users_query, many=True)
    if results:
        return results[0]['id']
    return

email = 'j.brito@ua.pt'

class ProfileSingle(Resource):

    #@jwt_required
    def get(self):
        header = request.headers
        #email = get_raw_jwt()['jti']

        users_query = Profile.query.filter_by(email=email)
        results = profile_schema.dump(users_query, many=True)
        return results

    #@jwt_required
    def post(self):
        raw_dict = request.get_json(force=True)
        try:
            profile_schema.validate(raw_dict)
            d_profile = raw_dict['data']['attributes']
            profile = Profile(d_profile['name'], d_profile['email'], d_profile['num_testes'], d_profile['register_date'], d_profile['picture'], d_profile['last_login'], d_profile['role'])
            profile.add(profile)
            query = profile_schema.query.get(profile.id)
            results = profile_schema.dump(query).data
            return results, 201

        except ValidationError as err:
            resp = jsonify({"error": err.messages})
            resp.status_code = 403
            return resp

        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = 403
            return resp

    def put(self):
        # email = get_raw_jwt()['jti']
        user_id =  retrieve_id(email)

        if not user_id:
            resp = jsonify({"error": 'Non-existent user'})
            resp.status_code = 403
            return resp

        raw_dict = request.get_json(force=True)
        try:
            profile = profile_schema.query.get(user_id)
            profile_schema.validate(raw_dict)
            d_profile = raw_dict['data']['attributes']

            profile['name'], profile['email'], profile['num_testes'], profile['register_date'], profile['picture'], profile['last_login'], profile['role'] = d_profile['name'], d_profile['email'], d_profile['num_testes'], d_profile['register_date'], d_profile['picture'], d_profile['last_login'], d_profile['role']

            profile.update(profile)
            results = profile
            return results, 201

        except ValidationError as err:
            resp = jsonify({"error": err.messages})
            resp.status_code = 403
            return resp

        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = 403
            return resp

    def delete(self):
        #email = get_raw_jwt()['jti']
        user_id = retrieve_id(email)

        if not user_id:
            resp = jsonify({"error": 'Non-existent user'})
            resp.status_code = 403
            return resp

        try:
            profile = profile_schema.query.get(user_id)

            profile.delete(profile)
            results = {profile}
            return results, 200

        except ValidationError as err:
            resp = jsonify({"error": err.messages})
            resp.status_code = 403
            return resp

        except SQLAlchemyError as e:
            db.session.rollback()
            resp = jsonify({"error": str(e)})
            resp.status_code = 403
            return resp

class RoleList(Resource):
    def get(self):
        role_query = Role.query.all()
        print("ROLE QUERYY ", role_query)
        results = profile_schema.dump(role_query, many=True)
        return results

class ExperienceList(Resource):

    def get(self):
        #email = get_raw_jwt()['jti']
        user_id = retrieve_id(email)
        experiences = Experience.query.filter_by(profile=user_id)
        results = experience_schema.dump(experiences, many=True)
        return results



api.add_resource(ProfileSingle, '/user')
api.add_resource(RoleList, '/role')
api.add_resource(ExperienceList, '/experience')