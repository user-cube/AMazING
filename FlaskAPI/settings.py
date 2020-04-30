import os
from dotenv import load_dotenv

load_dotenv()

pg_db_hostname = os.getenv('DB_HOST')
pg_db_name = os.getenv('DB_NAME')
pg_db_password = os.getenv('DB_PASS')
pg_db_username = os.getenv('DB_USER')

DEBUG = False
PORT = 5000
HOST = os.getenv('END_HOST')
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = "SOME SECRET"
# PostgreSQL
print(HOST)
SQLALCHEMY_DATABASE_URI = "postgresql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}".format(DB_USER=pg_db_username,
                                                                                        DB_PASS=pg_db_password,
                                                                                        DB_ADDR=pg_db_hostname,
                                                                                        DB_NAME=pg_db_name)


SQLALCHEMY_TRACK_MODIFICATONS = False


# JWT Decode CERT
with open("certificates/publicKey.pem", 'rb') as reader:
    JWT_SECRET_KEY = reader.read()


# JWT Decode Algorithm
JWT_DECODE_ALGORITHMS = ['RS256']


# JWT Identifier
JWT_IDENTITY_CLAIM = 'email'


