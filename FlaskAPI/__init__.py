from flask import Flask, Response
from flask_swagger_ui import  get_swaggerui_blueprint


class MyResponse(Response):
    default_mimetype = 'application/xml'


# http://flask.pocoo.org/docs/0.10/patterns/appfactories/
def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    app.config['SQLALCHEMY_TRACK_MODIFICATONS'] = False
    app.response_class = MyResponse

    from models import db
    db.init_app(app)

    # Blueprints
    from views import users_bp
    app.register_blueprint(users_bp)


    return app