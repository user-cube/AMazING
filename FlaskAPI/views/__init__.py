from views.nodes import NodeView, NodeInfoView, NodeInterfaceView, NodeAcessPoint
from views.roles import RoleView
from views.users import UserView, UserInfoView
from views.profiles import ProfileView
from views.experiences import ExperienceView, ExperienceInfoView, ExperienceScheduleView, ExperienceApuConfig

from flask import Blueprint
from flask_restful import Api


schema_blueprint = Blueprint('amazing', __name__)
api = Api(schema_blueprint)

#  All the endpoints

api.add_resource(UserView, '/user', '/user/')
api.add_resource(UserInfoView, '/user/<int:id>', '/user/<int:id>/')
api.add_resource(RoleView, '/role', '/role/')
api.add_resource(ProfileView, '/profile', '/profile/')
api.add_resource(ExperienceView, '/experience', '/experience/')
api.add_resource(ExperienceInfoView, '/experience/<int:id>', '/experience/<int:id>/')
api.add_resource(ExperienceApuConfig, '/experience/<int:experience_id>/node', '/experience/<int:experience_id>/node/',
                 '/experience/<int:experience_id>/node/<int:apu_config_id>', '/experience/<int:experience_id>/node/<int:apu_config_id>/')
api.add_resource(ExperienceScheduleView, '/experience/now', '/experience/now/')
api.add_resource(NodeView, '/node', '/node/')
api.add_resource(NodeInfoView, '/node/<int:id>', '/node/<int:id>/')
api.add_resource(NodeInterfaceView, '/node/<int:id>/<interface>/<command>',
                 '/node/<int:id>/<interface>/<command>/')
api.add_resource(NodeAcessPoint, '/node/<int:id>/accesspoint', '/node/<int:id>/accesspoint/')
