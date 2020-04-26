from dotenv import load_dotenv
import os

pg_db_hostname = os.getenv('DB_HOST')
pg_db_name = os.getenv('DB_NAME')
pg_db_password = os.getenv('DB_PASS')
pg_db_username = os.getenv('DB_USER')

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


SQLALCHEMY_TRACK_MODIFICATONS = False
""""
CERT = b-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAnzyis1ZjfNB0bBgKFMSv
vkTtwlvBsaJq7S5wA+kzeVOVpVWwkWdVha4s38XM/pa/yr47av7+z3VTmvDRyAHc
aT92whREFpLv9cj5lTeJSibyr/Mrm/YtjCZVWgaOYIhwrXwKLqPr/11inWsAkfIy
tvHWTxZYEcXLgAXFuUuaS3uF9gEiNQwzGTU1v0FqkqTBr4B8nW3HCN47XUu0t8Y0
e+lf4s4OxQawWD79J9/5d3Ry0vbV3Am1FtGJiJvOwRsIfVChDpYStTcHTCMqtvWb
V6L11BWkpzGXSW4Hv43qa+GSYOD2QU68Mb59oSk2OB+BtOLpJofmbGEGgvmwyCI9
MwIDAQAB
-----END PUBLIC KEY-----
"""

CERT = b'-----BEGIN PUBLIC KEY-----\n' \
       b'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAlc6LMgsz5b2m2Q3M/ps2\n' \
       b'XRKIuBRdwOUrY532F9OmkYrrdPsVpDpWTjRsc3Srrc9hUCIWNMQa++Cjq4yMFTHl\n' \
       b'D3Yn8x1kHJnO+DWw7sIJvg1+8PxZWZnslXUHjFRuuxUNUH5wxy5z/C1T6aMqIO93\n' \
       b'tXJty1q2nzVdW9GON0AI0oPHhSdPJalbxC7mo1ExZRa5SoYiBv8xe7ER4e1Neb3K\n' \
       b'sUF+Rfny1t79PQJC6uk0FwnloEQVj5yYvmwAv8HTda0mhFY0GdYqNk5+ks0D3hGg\n' \
       b'3D7FspI98MOX1lUatEJDq6/xE0JlK111uh24i7aZaZD5Bn3dqZl83zK4PdexXE/z\n' \
       b'JwIDAQAB\n' \
       b'-----END PUBLIC KEY-----'


# JWT Decode Algorithm
JWT_SECRET_KEY = CERT

JWT_DECODE_ALGORITHMS = ['RS256']
# JWT Decode CERT

# JWT Identifier
JWT_IDENTITY_CLAIM = 'email'


