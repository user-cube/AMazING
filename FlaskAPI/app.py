from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_raw_jwt
from views import schema_blueprint
from views import db

import requests

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


"""
@app.route('/ola')
@jwt_required
def hello_world():
    token = request.headers["Authorization"].split()[1]  # Split Bearer from token
    return 'Hello World!'

@app.route('/node/<nodeID>')
def node_info(nodeID):
    if nodeID=='1':
    	r = requests.get('http://192.168.1.141:5000/testi')
    	if r.status_code != 200:
    		msg = {'msg': 'Erro 200'}
    		return msg
    	return jsonify(r.json())
    	

    if nodeID=='2':
        r = requests.get('http://192.168.1.142:5000/testi')
        if r.status_code != 200:
            msg = {'msg': 'Erro 200'}
            return msg
        return jsonify(r.json())
"""

if __name__ == '__main__':
    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])
