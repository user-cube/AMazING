from flask_api import status

from app import app
from flask import json
from tests.test_base import encoded_user, encoded_admin  # encoded_admin has an invalid user


def test_profile_get():
    response = app.test_client().get(
        '/profile',
        headers={'Authorization': f'Bearer {encoded_user}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_200_OK
    assert data['name'] == 'TEST_USER'


def test_profile_get_no_content():
    response = app.test_client().get(
        '/profile',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_profile_update():
    response = app.test_client().put(
        '/profile',
        data=json.dumps({'name': 'insert_user', 'pic': 'picture file'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_user}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert data['name'] == 'insert_user'
    assert data['picture'] == 'picture file'


def test_profile_update_key_error():
    response = app.test_client().put(
        '/profile',
        data=json.dumps({'pic': 'picture file'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_user}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data['ERROR'] == "Missing key 'name'"


def test_profile_update_no_content():
    response = app.test_client().put(
        '/profile',
        data=json.dumps({'name': 'insert_user', 'pic': 'picture file'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'} #This email is not inserted in database
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
