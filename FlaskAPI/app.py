from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_raw_jwt
from views import schema_blueprint
from models import db
import requests
from dotenv import load_dotenv
import os
from flask_api import status

load_dotenv()
APU3 = os.getenv('apu3')
APU7 = os.getenv('apu7')
APU8 = os.getenv('apu8')
APU10 = os.getenv('apu10')

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
@app.route("/node/<nodeID>", methods=['GET'])
@jwt_required
def nodeInfo(nodeID):
    nodeID = int(nodeID)
    ip = ''
    if nodeID == 3: ip = APU3
    if nodeID == 7: ip = APU7
    if nodeID == 8: ip = APU8
    if nodeID == 10: ip = APU10

    print(ip)
    r = requests.get(ip + '/testi')

    if r.status_code != 200:
        return {'msg' : "Something went wrong"}, status.HTTP_400_BAD_REQUEST
    else:
        json = r.json()
        return jsonify(json)
"""

if __name__ == '__main__':
    app.run(host=app.config['END_HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])
