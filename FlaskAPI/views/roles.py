from models import Role, db
from flask import jsonify
from flask_restful import Resource


class RoleView(Resource):
    def get(self):
        role_query = db.session.query(Role).all()
        results = jsonify([role.serializable for role in role_query])
        return results
