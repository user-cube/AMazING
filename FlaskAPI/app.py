from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_raw_jwt
from views import schema_blueprint
from views import db

from settings import CERT

import jwt as tokenizer
import os
import requests
from dotenv import load_dotenv

app = Flask(__name__)
app.config.from_object('settings')

cors = CORS(app, resources={r"/*": {"origins": "*"}})
jwt = JWTManager(app)
app.config.update(JWT=jwt)

app.register_blueprint(schema_blueprint)

db.init_app(app)


@app.before_first_request
def create_database():
     db.create_all()

@app.route('/ola')
@jwt_required
def hello_world():
    token = request.headers["Authorization"].split()[1]  # Split Bearer from token
    return 'Hello World!'

@app.route('/nodes/<nodeID>')
def node_info(nodeID):
	r = requests.get('192.168.1.141')
	if r.status_code == 200:
		msg = {'msg': 'Erro 200'}
		return msg
	return jsonify(r.json())

@app.route('/node/<nodeID>')
def nodeInfo(nodeID):
    return jsonify(
                {'id': 1, 'placas': 2, 'ips': ['192.168.1.141', '192.168.1.03'],
                'mac': ['00:0a:95:9d:68:16', '00:0a:95:9d:68:17'],
                'state': 0
                }
            )



if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])
