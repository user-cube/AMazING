from _datetime import datetime

from flask import request, jsonify
from flask_restful import Resource, reqparse
from flask_api import status

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from models import Profile, db
from views.base import admin_required


#       Parse definition
parser = reqparse.RequestParser()
# users
parser.add_argument('typeID')
parser.add_argument('email')

# Users and Experience
parser.add_argument('content')


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
            db.session.rollback()
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
            db.session.rollback()
            results = jsonify({"ERROR": f" Missing key {err}"})
            results.status_code = status.HTTP_400_BAD_REQUEST
        return results

    """
    @admin_required
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
