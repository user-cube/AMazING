from flask_jwt_extended import JWTManager

from models import db

from flask import Flask, Response


class MyResponse(Response):
    default_mimetype = 'application/xml'

# http://flask.pocoo.org/docs/0.10/patterns/appfactories/
def create_app(config_filename):
    app = Flask(__name__)
    app.config.from_object(config_filename)
    app.config['SQLALCHEMY_TRACK_MODIFICATONS'] = False
    app.response_class = MyResponse

#    from models import db
#    db.init_app(app)

    # Blueprints
    from views import schema_blueprint
    app.register_blueprint(schema_blueprint)
    return app





app = create_app('settings')
db.init_app(app)
jwt = JWTManager(app)

@app.before_first_request
def create_database():
     db.create_all()

if __name__ == '__main__':

    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])