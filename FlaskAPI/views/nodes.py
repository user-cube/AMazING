from flask import request, jsonify, Blueprint
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from flask_api import status

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

import requests

from models import APU, db
from views.base import admin_required

nodes_blueprint = Blueprint('nodes', __name__, )


@nodes_blueprint.route('/node', methods=['GET'], strict_slashes=False)
def list_nodes():
    apu_query = db.session.query(APU).all()
    return jsonify([apu.serializable for apu in apu_query])


@nodes_blueprint.route('/node', methods=['POST'], strict_slashes=False)
@admin_required
def insert_node():
    raw_data = request.get_json(force=True)
    db.session.query(APU)
    try:
        if not 'port' in raw_data.keys() or not raw_data['port']:
            port = 5000
        else:
            port = raw_data['port']
        apu = APU(ip=raw_data['ip'], port=port, name=raw_data['name'])
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


# /node/<id>

@nodes_blueprint.route('/node/<int:id>', methods=['GET'], strict_slashes=False)
@jwt_required
def get_node(id):
    apu = db.session.query(APU).get(id)
    if not apu:
        results = jsonify({"ERROR": f"APU not found, id {id}"})
        results.status_code = status.HTTP_404_NOT_FOUND
        return results

    apu_request = f'http://{apu.ip}:{apu.port}/testi'
    try:
        results = requests.get(apu_request, timeout=2)
        return jsonify(results.json())
    except requests.exceptions.ConnectionError:
        results = jsonify({"ERROR": f"{apu.name}: not founded"})
        results.status_code = status.HTTP_444_CONNECTION_CLOSED_WITHOUT_RESPONSE
        return results


@nodes_blueprint.route('/node/<int:id>', methods=['PUT'], strict_slashes=False)
@admin_required
def alter_node(id):
    raw_data = request.get_json(force=True)
    apu = db.session.query(APU).get(id)
    if not apu:
        results = jsonify({"ERROR": f" Apu {id} not registered"})
        results.status_code = status.HTTP_204_NO_CONTENT
        return results
    try:
        if raw_data['name']:
            apu.name = raw_data['name']
        if raw_data['ip']:
            apu.ip = raw_data['ip']
        if raw_data['port']:
            apu.port = raw_data['port']
        apu.update()
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


@nodes_blueprint.route('/node/<int:id>', methods=['DELETE'], strict_slashes=False)
@admin_required
def delete_node(id):
    apu = db.session.query(APU).get(id)
    if not apu:
        results = jsonify({"ERROR": f"APU not found, id {id}"})
        results.status_code = status.HTTP_404_NOT_FOUND
        return results
    apu.delete(apu)
    return jsonify()


# PROXY Settings


@nodes_blueprint.route('/node/<int:id>/accesspoint', methods=['POST'], strict_slashes=False)
@jwt_required
def create_access_point(id):
    raw_data = request.get_json(force=True)
    apu = db.session.query(APU).get(id)
    if not apu:
        results = jsonify({"ERROR": f"APU not found, id {id}"})
        results.status_code = status.HTTP_404_NOT_FOUND
        return results

    apu_request = f'http://{apu.ip}:{apu.port}/newAP'
    try:
        response = requests.post(url=apu_request, json=raw_data, timeout=2)
        results = jsonify(response.json())
        results.status_code = response.status_code
        return results
    except requests.exceptions.ConnectionError:
        results = jsonify({"ERROR": f"{apu.name}: not founded"})
        results.status_code = status.HTTP_444_CONNECTION_CLOSED_WITHOUT_RESPONSE
        return results


@nodes_blueprint.route('/node/<int:id>/<interface>/<command>', methods=['GET'], strict_slashes=False)
@jwt_required
def send_node_command_to_interface(id, interface, command):
    apu = db.session.query(APU).get(id)
    if not apu:
        results = jsonify({"ERROR": f"APU not found, id {id}"})
        results.status_code = status.HTTP_404_NOT_FOUND
        return results

    apu_request = f'http://{apu.ip}:{apu.port}/{interface}/{command}'
    
    try:
        response = requests.get(apu_request, timeout=5)
        results = jsonify(response.json())
        results.status_code = response.status_code
        return results
    except requests.exceptions.ConnectionError:
        results = jsonify({"ERROR": f"{apu.name}: not found"})
        results.status_code = status.HTTP_444_CONNECTION_CLOSED_WITHOUT_RESPONSE
        return results


@nodes_blueprint.route('/node/<int:id>/<interface>/<command>', methods=['PUT', 'POST'], strict_slashes=False)
@jwt_required
def send_node_command__to_interface_as_post(id, interface, command):
    apu = db.session.query(APU).get(id)
    # apu = '127.0.0.1'
    raw_data = request.get_json(force=True)
    if not apu:
        results = jsonify({"ERROR": f"APU not found, id {id}"})
        results.status_code = status.HTTP_404_NOT_FOUND
        return results

    apu_request = f'http://{apu.ip}:{apu.port}/{interface}/{command}'
    iperf = f'http://{apu.ip}:{apu.port}/{command}'
    if command == "connect":
        try:
            ssid = raw_data['SSID']
            password = raw_data['password']
            response = requests.post(url=apu_request, json={'SSID': ssid, 'PASS' : password}, timeout=60)
            results = jsonify(response.json())
            results.status_code = response.status_code
            return results
        except requests.exceptions.ConnectionError:
            results = jsonify({"ERROR": f"{apu.name}: not founded"})
            results.status_code = status.HTTP_444_CONNECTION_CLOSED_WITHOUT_RESPONSE
            return results
    if command == "iperfsv3":
        try:
            port = raw_data['port']
            ip = raw_data['ip']
            mtu = raw_data['mtu']
            response = requests.post(url=iperf, json={'port' : port, 'ip' : ip, 'mtu' : mtu}, timeout=60)
            results = jsonify(response.json())
            results.status_code = response.status_code
            return results
        except requests.exceptions.ConnectionError:
            results = jsonify({"ERROR": f"{apu.name}: not founded"})
            results.status_code = status.HTTP_444_CONNECTION_CLOSED_WITHOUT_RESPONSE
            return results
    if command == "iperfclient":
        try:
            port = raw_data['port']
            ip = raw_data['ip']
            mtu = raw_data['mtu']
            response = requests.post(url=iperf, json={'port' : port, 'ip' : ip, 'mtu' : mtu}, timeout=60)
            results = jsonify(response.json())
            results.status_code = response.status_code
            return results
        except requests.exceptions.ConnectionError:
            results = jsonify({"ERROR": f"{apu.name}: not founded"})
            results.status_code = status.HTTP_444_CONNECTION_CLOSED_WITHOUT_RESPONSE
            return results
    else:   
        try:
            ip = raw_data['ip']
            response = requests.post(url=apu_request, json={'ip': ip}, timeout=5)
            results = jsonify(response.json())
            results.status_code = response.status_code
            return results
        except requests.exceptions.ConnectionError:
            results = jsonify({"ERROR": f"{apu.name}: not founded"})
            results.status_code = status.HTTP_444_CONNECTION_CLOSED_WITHOUT_RESPONSE
            return results