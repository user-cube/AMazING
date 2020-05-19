from flask import jsonify
from flask_api import status
from functools import wraps
from flask_jwt_extended import verify_jwt_in_request, get_raw_jwt

from models import Profile, db


def get_user_by_email(email):
    users_query = db.session().query(Profile).filter(Profile.email == email).one()
    return users_query


def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        jwt_data = get_raw_jwt()
        if not jwt_data['isAdmin']:
            results = jsonify({'ERROR': 'AUTHORIZATION_ERROR', 'CONTENT': 'Forbidden access, admins only!'})
            results.status_code = status.HTTP_403_FORBIDDEN
            return results
        else:
            return fn(*args, **kwargs)

    return wrapper

    # Exceptions


class BaseException(Exception):
    def __init__(self, *args):
        if args:
            self.messages = args[0]
        else:
            self.messages = None


class UnauthorizedException(BaseException):

    def __str__(self):
        if self.messages:
            return f'Unauthorized Access, {self.messages}'
        else:
            return 'Unauthorized access for select content'


class ExperienceScheduleException(BaseException):

    def __str__(self):
        if self.messages:
            return f'Range time already busy, experiences {self.messages}'
        else:
            return 'Range time already busy'


class FailedExperienceException(BaseException):

    def __str__(self):
        if self.messages:
            return f'Failed detected while running experience: {self.messages}'
        else:
            return 'Failed detected while running experience'
