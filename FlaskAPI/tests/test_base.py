import os, jwt

from app import app


with open(os.path.join(app.config['BASE_DIR'], 'FlaskAPI/certificates/privateKey.pem'), 'rb') as reader:
    private_key = reader.read()

encoded_admin = jwt.encode({'email': 'invalid@email.com', 'isAdmin': True}, private_key, algorithm='RS256').decode('utf-8')
encoded_user = jwt.encode({'email': 'testuser@test.com', 'isAdmin': False}, private_key, algorithm='RS256').decode('utf-8')