from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
session = None
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

    @property
    def serializable(self):
        return {
            'id': self.id,
            'role_name': self.role_name,
        }


class Profile(db.Model, CRUD):

    __tablename__ = 'profile'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    num_test = db.Column(db.INTEGER, nullable=True)
    register_date = db.Column(db.TIMESTAMP, nullable=False)
    picture = db.Column(db.String(10485760), nullable=True)
    last_login = db.Column(db.TIMESTAMP, nullable=True)
    role = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __init__(self,  name, email, register_date, role, num_test=None, picture=None, last_login=None):
        self.name = name
        self.email = email
        self.num_test = num_test
        self.register_date = register_date
        self.picture = picture
        self.last_login = last_login
        self.role = role

    def __repr__(self):
        return '<user: {}, Email: {}, Role: {}'.format(self.name, self.email, self.role)

    @property
    def serializable(self):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "num_test": self.num_test,
            "register_date": self.register_date.strftime("%Y-%m-%d %H:%M:%S"),
            "picture": self.picture,
            "last_login": self.last_login,
            "role": self.role
        }


class Template(db.Model, CRUD):

    __tablename__ = 'template'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    duration = db.Column(db.BIGINT)
    profile = db.Column(db.Integer, db.ForeignKey('profile.id'))

    def __init__(self, id, name, duration, profile):
        self.id = id
        self.name = name
        self.duration = duration
        self.profile = profile

    @property
    def serializable(self):
        return {
            "id": self.id,
            "name": self.name,
            "duration": self.duration,
            "profile": self.profile
        }


class Experience(db.Model, CRUD):

    __tablename__ = 'experience'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    begin_date = db.Column(db.TIMESTAMP, nullable=False)
    end_date = db.Column(db.TIMESTAMP, nullable=False)
    num_test = db.Column(db.Integer, nullable=False)
    register_date = db.Column(db.TIMESTAMP, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    profile = db.Column(db.Integer, db.ForeignKey('profile.id'))
    template = db.Column(db.Integer, db.ForeignKey('template.id'))

    def __init__(self, name, begin_date, end_date, num_test, register_date, status, profile, template):
        self.name = name
        self.begin_date = begin_date
        self.end_date = end_date
        self.num_test = num_test
        self.register_date = register_date
        self.status = status
        self.profile = profile
        self.template = template

    @property
    def serializable(self):
        return {
            "id": self.id,
            "name": self.name,
            "begin_date": self.begin_date.strftime("%Y-%m-%d %H:%M:%S"),
            "end_date": self.end_date.strftime("%Y-%m-%d %H:%M:%S"),
            "num_test": self.num_test,
            "register_date": self.register_date.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status,
            "profile": self.profile,
            "template": self.template
        }


class APU(db.Model, CRUD):

    __tablename__ = 'apu'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(20), unique=True)
    name = db.Column(db.String(10))

    def __init__(self, ip, name):
        self.ip = ip
        self.name = name

    @property
    def serializable(self):
        return {
            "id": self.id,
            "ip": self.ip,
            "name": self.name
        }


class APUConfig(db.Model, CRUD):

    __tablename__ = 'apuconfig'
    id = db.Column(db.Integer, primary_key=True)
    apu = db.Column(db.Integer, db.ForeignKey('apuconfig.id'))
    ip = db.Column(db.String(40))
    protocol = db.Column(db.String(50))
    base_template = db.Column(db.Integer)

    def __init__(self, apu, ip, protocol, base_template):
        self.apu = apu
        self.ip = ip
        self.protocol = protocol
        self.base_template = base_template

    def serializable(self):
        return {
            "id": self.id,
            "apu": self.apu,
            "ip": self.ip,
            "protocol": self.protocol,
            "base_template": self.base_template
        }

class APUConfig_Template(db.Model, CRUD):

    __tablename__ = 'apuconfig_template'
    id = db.Column(db.Integer, primary_key=True)
    apu_config = db.Column(db.Integer, db.ForeignKey('apuconfig.id'))
    template = db.Column(db.Integer, db.ForeignKey('template.id'))

    def __init__(self, apu_config, template):
        self.apu_config = apu_config
        self.template = template

    @property
    def serializable(self):
        return {
            "apu_config": self.apu_config,
            "template": self.template
        }
