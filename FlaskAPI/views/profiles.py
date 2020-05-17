from flask import request, jsonify
from flask_jwt_extended import get_raw_jwt, jwt_required
from flask_restful import Resource
from flask_api import status

from sqlalchemy.exc import SQLAlchemyError

from models import Profile, db


class ProfileView(Resource):
    @jwt_required
    def get(self):
        jwt_raw = get_raw_jwt()
        email = jwt_raw['email']
        try:
            profile = db.session.query(Profile).filter(Profile.email == email).one()
            results = profile.serializable
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
                user.picture = str.encode(raw_data['pic'])
            user.name = raw_data['name']
            db.session.commit()
            results = jsonify(user.serializable)
            results.status_code = status.HTTP_202_ACCEPTED
        except KeyError as err:
            db.session.rollback()
            results = jsonify({"ERROR": f" Missing key {err}"})
            results.status_code = status.HTTP_400_BAD_REQUEST
        return results

