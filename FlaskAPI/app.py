from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager

from tests.insert_data import insert_db_info
from views.experiences import experiences_blueprint
from views.nodes import nodes_blueprint
from views.profiles import profiles_blueprint
from views.roles import roles_blueprint
from views.users import users_blueprint
from models import db

app = Flask(__name__)
app.config.from_object('settings')

cors = CORS(app, resources={r"/*": {"origins": "*"}})
jwt = JWTManager(app)
app.config.update(JWT=jwt)

app.register_blueprint(experiences_blueprint)
app.register_blueprint(nodes_blueprint)
app.register_blueprint(profiles_blueprint)
app.register_blueprint(roles_blueprint)
app.register_blueprint(users_blueprint)

db.init_app(app)


@app.before_first_request
def create_database():
    db.create_all()
    if app.config['TESTING']:
        insert_db_info(db)

#@app.before_first_request
    #schedulling the next experience


if __name__ == '__main__':
    app.run(host=app.config['END_HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])


