import os
from dotenv import load_dotenv

load_dotenv()


"""
                        Server Configuration Session
"""

# Server Info
DEBUG = os.getenv('DEBUG') == 'True'
PORT = os.getenv('PORT')
END_HOST = os.getenv('END_HOST')

TESTING = os.getenv('TESTING') == 'True'


"""
                        DataBase Session
"""

if not TESTING:
    # BD Info
    DB_HOST = os.getenv('DB_HOST')
    DB_NAME = os.getenv('DB_NAME')
    DB_PASSWORD = os.getenv('DB_PASS')
    DB_USERNAME = os.getenv('DB_USER')

    # PostgreSQL
    SQLALCHEMY_DATABASE_URI = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

else:
    #InMemory Database
    SQLALCHEMY_DATABASE_URI = os.getenv('TEST_DB')


SQLALCHEMY_ECHO = os.getenv('SQLALCHEMY_ECHO') == 'True'
SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS') == 'True'


"""
                        Json Web Token Session
"""

# JWT Decode CERT
with open("certificates/publicKey.pem", 'rb') as reader:
    JWT_SECRET_KEY = reader.read()

# These info are common between all environment

# JWT Decode Algorithm
JWT_DECODE_ALGORITHMS = ['RS256']

# JWT Identifier
JWT_IDENTITY_CLAIM = 'email'


"""
                        Mail session
"""

MAIL_SERVER = os.getenv('MAIL_HOST')
MAIL_PORT = os.getenv('MAIL_PORT')
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = os.getenv('MAIL_USERNAME')
MAIL_PASSWORD = os.getenv('MAIL_PASS')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_SENDER')
MAIL_DEBUG = True
MAIL_SUPPRESS_SEND = False


"""
                        Swagger Session
"""
SWAGGER_URL = ''
API_URL = '/static/swagger.json'
APP_NAME = 'AMazING api Documentation'



