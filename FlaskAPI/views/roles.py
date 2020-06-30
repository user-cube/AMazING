from flask_api import status
from marshmallow import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm.exc import NoResultFound

from models import Role, db
from flask import jsonify, request, Blueprint

from views.base import admin_required

roles_blueprint = Blueprint('role', __name__,)


@roles_blueprint.route('/role', methods=['GET'], strict_slashes=False)
def list_roles():
    role_query = db.session.query(Role).all()
    results = jsonify([role.serializable for role in role_query])
    return results


@roles_blueprint.route('/role', methods=['POST'], strict_slashes=False)
@admin_required
def insert_role():
    raw_data = request.get_json(force=True)
    try:
        role = Role(role_name=raw_data['name'])
        role.add(role)
        results = jsonify(role.serializable)
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
        results = jsonify({"ERROR": f"Missing key {err}"})
        results.status_code = status.HTTP_400_BAD_REQUEST
    return results


@roles_blueprint.route('/role/<int:id>', methods=['GET'], strict_slashes=False)
def get_role():
    try:
        roles_query = db.session.query(Role).get(id)
        if not roles_query:
            raise NoResultFound
        results = jsonify(roles_query.serializable)

    except NoResultFound:
        results = jsonify({'ERROR': f'Item not found {id}'})
        results.status_code = status.HTTP_404_NOT_FOUND
    return results


@roles_blueprint.route('/role/<int:id>', methods=['PUT'], strict_slashes=False)
@admin_required
def alter_role(id):
    raw_data = request.get_json(force=True)
    try:
        role = db.session.query(Role).get(id)
        if not role:
            raise NoResultFound
        role.role_name = raw_data['name']
        role.update()
        results = jsonify(role.serializable)

    except ValidationError as err:
        results = jsonify({"error": err.messages})
        results.status_code = status.HTTP_403_FORBIDDEN

    except SQLAlchemyError as err:
        db.session.rollback()
        results = jsonify({"error": str(err)})
        results.status_code = status.HTTP_400_BAD_REQUEST

    except KeyError as err:
        db.session.rollback()
        results = jsonify({"ERROR": f"Missing key {err}"})
        results.status_code = status.HTTP_400_BAD_REQUEST

    except NoResultFound:
        db.session.rollback()
        results = jsonify({"ERROR": f'Item not found role id: {id}'})
        results.status_code = status.HTTP_404_NOT_FOUND

    return results


@roles_blueprint.route('/role/<int:id>', methods=['DELETE'], strict_slashes=False)
@admin_required
def delete_role(id):
    try:
        role = db.session.query(Role).get(id)
        if not role:
            raise NoResultFound
        role.delete(role)
        results = jsonify(role.serializable)

    except ValidationError as err:
        results = jsonify({"error": err.messages})
        results.status_code = status.HTTP_403_FORBIDDEN

    except SQLAlchemyError as err:
        db.session.rollback()
        results = jsonify({"error": str(err)})
        results.status_code = status.HTTP_400_BAD_REQUEST

    except KeyError as err:
        db.session.rollback()
        results = jsonify({"ERROR": f"Missing key {err}"})
        results.status_code = status.HTTP_400_BAD_REQUEST

    except NoResultFound:
        db.session.rollback()
        results = jsonify({"ERROR": f'Item not found role id: {id}'})
        results.status_code = status.HTTP_404_NOT_FOUND

    return results

