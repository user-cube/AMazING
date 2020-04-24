from datetime import datetime, timedelta, timezone

from jwt import (
    JWT,
    jwk_from_pem,
)
from jwt.utils import get_int_from_datetime
jwtManager = JWT()
with open("app/certificates/privateKey.pem", 'rb') as reader:
    private_key = jwk_from_pem(reader.read())

with open("app/certificates/publicKey.pem", 'rb') as reader:
    public_key = jwk_from_pem(reader.read())

class Tokenizer:
    def __init__(self):
        self.private_key = private_key
        self.public_key = public_key

    def gerateEmailToken(self, email):
        message = {
            'email': email,
            'iat': get_int_from_datetime(datetime.now(timezone.utc)),
            'exp': get_int_from_datetime(
                datetime.now(timezone.utc) + timedelta(minutes=1)),
        }
        return jwtManager.encode(message, self.private_key, alg='RS256')

    def generateValidation(self, email):
        message = {
            'email': email,
            'iat': get_int_from_datetime(datetime.now(timezone.utc)),
            'exp': get_int_from_datetime(
                datetime.now(timezone.utc) + timedelta(hours=24)),
        }
        return jwtManager.encode(message, self.private_key, alg='RS256')

    def checkToken(self, token):
        try:
            decoded = jwtManager.decode(message=token, key=public_key)
            return decoded['email']
        except:
            return None