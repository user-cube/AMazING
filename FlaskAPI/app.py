from flask import Flask
import logging
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint

from schedule.experience_schedule import experience_scheduler_manager
from tests.insert_data import insert_db_info
from views.experiences import experiences_blueprint
from views.nodes import nodes_blueprint
from views.profiles import profiles_blueprint
from views.roles import roles_blueprint
from views.users import users_blueprint
from models import db

app = Flask(__name__)
app.config.from_object('settings')

"""
            Json Web Token
"""

cors = CORS(app, resources={r"/*": {"origins": "*"}})
jwt = JWTManager(app)
app.config.update(JWT=jwt)

"""
            views
"""

app.register_blueprint(experiences_blueprint)
app.register_blueprint(nodes_blueprint)
app.register_blueprint(profiles_blueprint)
app.register_blueprint(roles_blueprint)
app.register_blueprint(users_blueprint)


"""
            Swagger
"""

SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    app.config['SWAGGER_URL'],
    app.config['API_URL'],
    config={
        'app_name': app.config['APP_NAME']
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=app.config['SWAGGER_URL'])

db.init_app(app)

logging.basicConfig(level=logging.DEBUG)

@app.before_first_request
def create_database():
    with app.app_context():
        db.create_all()
    if app.config['TESTING']:
        insert_db_info()


@app.before_first_request
def schedule_experience():
    experience_scheduler_manager.configure(app=app, db=db)
    experience_scheduler_manager.manage_next_experience()


if __name__ == '__main__':
    app.run(host=app.config['END_HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])
