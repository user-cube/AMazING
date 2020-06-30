from flask import request, jsonify, Blueprint
from flask_jwt_extended import get_raw_jwt, jwt_required
from flask_api import status

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from models import Profile, db

profiles_blueprint = Blueprint('profiles', __name__,)

@profiles_blueprint.route('/profile', methods=['GET'], strict_slashes=False)
@jwt_required
def get_profile():
    jwt_raw = get_raw_jwt()
    email = jwt_raw['email']
    try:
        profile = db.session.query(Profile).filter(Profile.email == email).one()
        results = profile.serializable
    except SQLAlchemyError:
        results = jsonify({"ERROR": f"User email not registered, email: '{email}'"})
        results.status_code = status.HTTP_204_NO_CONTENT
    return results


@profiles_blueprint.route('/profile', methods=['PUT'], strict_slashes=False)
@jwt_required
def alter_profile():
    email = get_raw_jwt()['email']
    raw_data = request.get_json(force=True)
    try:
        user = db.session().query(Profile).filter(Profile.email == email).one()
        if raw_data['pic']:
            user.picture = str.encode(raw_data['pic'])
        user.name = raw_data['name']
        user.update()
        results = jsonify(user.serializable)
        results.status_code = status.HTTP_202_ACCEPTED
    except KeyError as err:
        db.session.rollback()
        results = jsonify({"ERROR": f"Missing key {err}"})
        results.status_code = status.HTTP_400_BAD_REQUEST
    except SQLAlchemyError:
        results = jsonify({"ERROR": f"User email not registered, email: '{email}'"})
        results.status_code = status.HTTP_204_NO_CONTENT
    return results