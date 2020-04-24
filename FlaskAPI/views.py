from models import *
from flask import Blueprint, request, jsonify, make_response
from flask_restful import Api, Resource

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

users_bp = Blueprint('users', __name__)
api = Api(users_bp)

role_schema = RoleSchema()
profile_schema = ProfileSchema(many=True)
template_schema = TemplateSchema(many=True)
experience_schema = ExperienceSchema(many=True)
apu_schema = APUSchema(many=True)
apuconfig_schema = APUConfigSchema(many=True)
apuconfig_template_schema = APUConfig_TemplateSchema(many=True)


class ProfileList(Resource):
    def get(self):
        users_query = Profile.query.all()
        results = profile_schema.dump(users_query, many=True).data
        return results

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

class RoleList(Resource):
    def get(self):
        role_query = Role.query.all()
        results = profile_schema.dump(role_query, many=True).data
        return results


api.add_resource(ProfileList, '/users')
api.add_resource(RoleList, '/roles')