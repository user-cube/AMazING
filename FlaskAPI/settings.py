import os

# DATABASE SETTINGS

pg_db_username = os.environ.get('db_username')
pg_db_password = os.environ.get('db_password')
pg_db_name     = os.environ.get('db_name')
pg_db_hostname = os.environ.get('db_hostname')


DEBUG = True
PORT = 5000
HOST = "127.0.0.1"
SQLALCHEMY_ECHO = True
SQLALCHEMY_TRACK_MODIFICATIONS = True
SECRET_KEY = "SOME SECRET"
# PostgreSQL
SQLALCHEMY_DATABASE_URI = "postgresql://{DB_USER}:{DB_PASS}@{DB_ADDR}/{DB_NAME}".format(DB_USER=pg_db_username,
                                                                                        DB_PASS=pg_db_password,
                                                                                        DB_ADDR=pg_db_hostname,
                                                                                        DB_NAME=pg_db_name)




# JWT Decode Algorithm

jwt_cert       = os.environ.get('cert')


JWT_DECODE_ALGORITHMS = 'RS256'
# JWT Decode CERT
JWT_SECRET_KEY = jwt_cert
# JWT Identifier
JWT_IDENTITY_CLAIM = 'email'