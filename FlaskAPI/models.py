from flask_sqlalchemy import SQLAlchemy
from marshmallow import validate
from marshmallow_jsonapi import Schema, fields
from flask_marshmallow import Marshmallow
from marshmallow import Schema, fields, ValidationError, pre_load

db = SQLAlchemy()

class CRUD:
    def add(self, resource):
        db.session.add(resource)
        return db.session.commit()

    def update(self):
        return db.session.commit()

    def delete(self, resource):
        db.session.delete(resource)
        return db.session.commit()


class Role (db.Model, CRUD):

    __tablename__ = 'role'
    id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(20))

    def __init__(self, role_name):
        self.role_name = role_name


class Profile(db.Model, CRUD):

    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    num_testes = db.Column(db.INTEGER)
    register_date = db.Column(db.TIMESTAMP, nullable=False)
    picture = db.Column(db.LargeBinary)
    last_login = db.Column(db.TIMESTAMP)
    role = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __init__(self, id, name, email, num_testes, register_date, picture, last_login, role):
        self.id = id
        self.name = name
        self.email = email
        self.num_testes = num_testes
        self.register_date = register_date
        self.picture = picture
        self.last_login = last_login
        self.role = role


class Template(db.Model, CRUD):

    __tablename__ = 'template'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    protocol = db.Column(db.String(50))
    duration = db.Column(db.BIGINT)
    profile = db.Column(db.Integer, db.ForeignKey('profile.id'))

    def __init__(self, id, name, protocol, duration, profile):
        self.id = id
        self.name = name
        self.protocol = protocol
        self.duration = duration
        self.profile = profile


class Experience(db.Model, CRUD):

    __tablename__ = 'experience'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    begin_date = db.Column(db.TIMESTAMP, nullable=False)
    end_date = db.Column(db.TIMESTAMP, nullable=False)
    num_test = db.Column(db.Integer)
    register_date = db.Column(db.TIMESTAMP, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    profile = db.Column(db.Integer, db.ForeignKey('profile.id'))
    template = db.Column(db.Integer, db.ForeignKey('template.id'))

    def __init__(self, id, name, begin_date, end_date, num_test, register_date, status, profile, template):
        self.id = id
        self.name = name
        self.begin_date = begin_date
        self.end_date = end_date
        self.num_test = num_test
        self.register_date = register_date
        self.status = status
        self.profile = profile
        self.template = template


class APU(db.Model, CRUD):

    __tablename__ = 'apu'
    number = db.Column(db.Integer, primary_key=True)

    def __init__(self, number):
        self.number = number


class APUConfig(db.Model, CRUD):

    __tablename__ = 'apuconfig'
    id = db.Column(db.Integer, primary_key=True)


class APUConfig_Template(db.Model, CRUD):

    __tablename__ = 'apuconfig_template'
    id_nonexistent = db.Column(db.Integer, primary_key=True)
    apu = db.Column(db.Integer, db.ForeignKey('apu.number'))
    apu_config = db.Column(db.Integer, db.ForeignKey('apuconfig.id'))
    template = db.Column(db.Integer, db.ForeignKey('template.id'))

    def __init__(self, apu, apu_config, template):
        self.apu = apu
        self.apu_config = apu_config
        self.template = template


class RoleSchema(Schema):
    class Meta:
        fields = ('id', 'role_name')


class ProfileSchema(Schema):
    class Meta:
        fields = ('id', 'name', 'email', 'num_testes', 'register_date', 'picture', 'last_login', 'role')


class TemplateSchema(Schema):
    class Meta:
        fields = ('Template', 'id', 'name', 'protocol', 'duration', 'profile')


class ExperienceSchema(Schema):
    class Meta:
        fields = ('id', 'name', 'begin_date', 'end_date', 'num_test', 'register_date', 'status', 'profile', 'template')


class APUSchema(Schema):
    class Meta:
        fields = ('number',)


class APUConfigSchema(Schema):
    class Meta:
        fields = ('id',)


class APUConfig_TemplateSchema(Schema):
    class Meta:
        fields = ('apu', 'apu_config', 'template')



