from flask import request, jsonify
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from flask_api import status

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

import requests

from models import APU, db
from views.base import admin_required


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

        except KeyError as err:
            db.session.rollback()
            results = jsonify({"ERROR": f" Missing key {err}"})
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
        except SQLAlchemyError as err:
            db.session.rollback()
            results = jsonify({"ERROR": str(err)})
            results.status_code = status.HTTP_400_BAD_REQUEST
        except KeyError as err:
            db.session.rollback()
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

