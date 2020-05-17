from flask_jwt_extended import get_raw_jwt, jwt_required

from flask import request, jsonify
from flask_restful import Resource, reqparse
from flask_api import status

from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from models import db, Template, APU_Config, Profile
from views.base import get_user_by_email

parser = reqparse.RequestParser()
# Users and Experience
parser.add_argument('content')

# Experience
parser.add_argument('userID')
parser.add_argument('date')
parser.add_argument('begin_date')
parser.add_argument('end_date')
parser.add_argument('status')


class TemplateView(Resource):
    @jwt_required
    def get(self):
        parse_data = parser.parse_args()
        return jsonify(self.template_query(parse_data))

    @jwt_required
    def post(self):
        raw_data = request.get_json(force=True)
        try:
            jwt_data = get_raw_jwt()
            user_id = get_user_by_email(jwt_data['email']).id
            template = Template(profile=user_id, duration=raw_data['template']['duration'],
                                name=raw_data['template']['name'])
            template.add(template)
            for apu_config_item in raw_data['config_list']:
                apu_config = APU_Config(
                    apu=apu_config_item['apu'],
                    ip=apu_config_item['ip'],
                    protocol=apu_config_item['protocol'],
                    base_template=apu_config_item['base_template'],
                    template=template.id)
                apu_config.add(apu_config)
                results = jsonify(self.template_query(parser_data=None, id=template.id))
                results.status_code = status.HTTP_201_CREATED

        except ValidationError as err:
            results = jsonify({"ERROR": err.messages})
            results.status_code = status.HTTP_403_FORBIDDEN
        except SQLAlchemyError as e:
            db.session.rollback()
            results = jsonify({"ERROR": str(e)})
            results.status_code = status.HTTP_400_BAD_REQUEST
        except KeyError as err:
            db.session.rollback()
            results = jsonify({"ERROR": f" Missing key {err}"})
            results.status_code = status.HTTP_400_BAD_REQUEST

        return results

    @staticmethod
    def template_query(parse_data, id=None):
        templates_query = db.session.query(Template, Profile, APU_Config) \
            .filter(Template.profile == Profile.id) \
            .filter(Template.id == APU_Config.template)
        # Apply filters

        if id:
            templates_query = templates_query.filter(Template.id == id)
        else:
            if parse_data['userID']:
                templates_query = templates_query.filter(Template.profile == parse_data['userID'])
            if parse_data['content']:
                templates_query = templates_query.filter(Template.name.contains(parse_data['content']))
        query_results = templates_query.all()

        response = {}
        for template, profile, apu_config in query_results:
            if not template in response.keys():
                response[template] = {'author': profile, 'config': []}
            response[template]['config'].append(apu_config.serializable)
        results = []
        for template in response.keys():
            results.append({'template': template.serializable, 'author': response[template]['author'].name,
                            'config_list': response[template]['config']})
        return results


class TemplateInfoView(Resource):
    def get(self, id):
        parse_data = parser.parse_args()
        results = TemplateView.template_query(parse_data, id)
        return jsonify(results[0])
