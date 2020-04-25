from flask import Flask, request, render_template, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required
from settings import CERT

import jwt as tokenizer
import os
from dotenv import load_dotenv

app = Flask(__name__)

# JWT Decode Algorithm
app.config['JWT_DECODE_ALGORITHMS'] = ['RS256']
# JWT Decode CERT
app.config['JWT_SECRET_KEY'] = CERT
# JWT Identifier
app.config['JWT_IDENTITY_CLAIM'] = 'email'

cors = CORS(app, resources={r"/*": {"origins": "*"}})
jwt = JWTManager(app)

@app.route('/')
@jwt_required
def hello_world():
    token = request.headers["Authorization"].split()[1]  # Split Bearer from token
    return 'Hello World!'


if __name__ == '__main__':
    app.run()
