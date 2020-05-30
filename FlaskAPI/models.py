from flask_sqlalchemy import SQLAlchemy
import base64

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


class Role(db.Model, CRUD):
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
    picture = db.Column(db.LargeBinary, nullable=True)
    last_login = db.Column(db.TIMESTAMP, nullable=True)
    role = db.Column(db.Integer, db.ForeignKey('role.id'))

    def __init__(self, name, email, register_date, role, num_test=None, picture=None, last_login=None):
        self.name = name
        self.email = email
        self.num_test = num_test
        self.register_date = register_date
        self.picture = picture
        self.last_login = last_login
        self.role = role

    # def __repr__(self):
    #    return '<user: {}, Email: {}, Role: {}'.format(self.name, self.email, self.role)

    @property
    def serializable(self):
        if self.picture:
            pic = self.picture.decode("utf-8")
        else:
            pic = None
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "num_test": self.num_test,
            "register_date": self.register_date.strftime("%Y-%m-%d %H:%M:%S"),
            "picture": pic,
            "last_login": self.last_login,
            "role": self.role
        }


class Experience(db.Model, CRUD):
    __tablename__ = 'experience'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    begin_date = db.Column(db.TIMESTAMP, nullable=False)
    end_date = db.Column(db.TIMESTAMP, nullable=False)
    register_date = db.Column(db.TIMESTAMP, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    profile = db.Column(db.Integer, db.ForeignKey('profile.id'))

    def __init__(self, name, begin_date, end_date, register_date, status, profile):
        self.name = name
        self.begin_date = begin_date
        self.end_date = end_date
        self.register_date = register_date
        self.status = status
        self.profile = profile

    @property
    def serializable(self):
        return {
            "id": self.id,
            "name": self.name,
            "begin_date": self.begin_date.strftime("%Y-%m-%d %H:%M:%S"),
            "end_date": self.end_date.strftime("%Y-%m-%d %H:%M:%S"),
            "register_date": self.register_date.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status,
            "profile": self.profile
        }


class ExperienceStatus:
    SCHEDULED = 'SCHEDULED'
    RUNNING = 'RUNNING'
    SUSPENDED = 'SUSPENDED'
    FINISHED = 'FINISHED'
    CANCELED = 'CANCELED'
    FAILED = 'FAILED'


class APU(db.Model, CRUD):
    __tablename__ = 'apu'
    id = db.Column(db.Integer, primary_key=True)
    ip = db.Column(db.String(20))
    port = db.Column(db.Integer)
    name = db.Column(db.String(10))

    db.UniqueConstraint('ip', 'port', name='apu_ip_port_key')

    def __init__(self, ip, port, name):
        self.ip = ip
        self.port = port
        self.name = name

    @property
    def serializable(self):
        return {
            "id": self.id,
            "ip": self.ip,
            "port": self.port,
            "name": self.name
        }


class APU_Config(db.Model, CRUD):
    __tablename__ = 'apu_config'
    id = db.Column(db.Integer, primary_key=True)
    apu = db.Column(db.Integer, db.ForeignKey('apu.id'))
    file = db.Column(db.LargeBinary, nullable=True)
    experience = db.Column(db.Integer, db.ForeignKey('experience.id'))
    db.UniqueConstraint('apu', 'experience', name='apu_config_experience_apu_key')

    def __init__(self, apu, file, experience):
        self.apu = apu
        self.file = file
        self.experience = experience

    # def __repr__(self):
    #     return f'<apu = {self.apu}, ip = {self.ip}, protocol = {self.protocol}, base_template = {self.base_template}, template = {self.template}>'
    @property
    def serializable(self):
        if self.file:
            f = self.file.decode("utf-8")
        else:
            f = None
        return {
            "id": self.id,
            "apu": self.apu,
            "experience": self.experience,
            "file": f
        }
