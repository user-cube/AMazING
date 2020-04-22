from datetime import datetime, timedelta, timezone

from jwt import (
    JWT,
    jwk_from_pem,
)
from jwt.utils import get_int_from_datetime
jwtManager = JWT()
with open("app/certificates/privateKey.pem", 'rb') as reader:
    input_key = jwk_from_pem(reader.read())

class Tokenizer:
    def __init__(self):
        self.key = input_key

    def gerateEmailToken(self, email):
        message = {
            'email': email,
            'iat': get_int_from_datetime(datetime.now(timezone.utc)),
            'exp': get_int_from_datetime(
                datetime.now(timezone.utc) + timedelta(minutes=1)),
        }
        return jwtManager.encode(message, input_key, alg='RS256')