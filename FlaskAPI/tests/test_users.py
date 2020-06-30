from _datetime import datetime

from flask_api import status

from app import app
from flask import json
from tests.test_base import encoded_user, encoded_admin


def test_user_admin_token():
    response = app.test_client().get(
        '/user',
        headers={'Authorization': f'Bearer {encoded_user}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_user_list():
    response = app.test_client().get(
        '/user',
        headers={'Authorization': f'Bearer {encoded_admin}'},
        query_string={'typeID': 1, 'email': 'testuser', 'content': 'insert'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)

    assert response.status_code == 200
    assert isinstance(data, list)
    assert len(data) > 0


def test_user_get():
    response = app.test_client().get(
        '/user/1',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)

    assert response.status_code == status.HTTP_200_OK
    assert data['name'] == 'insert_user'
    assert data['email'] == 'testuser@test.com'
    assert data['role'] == 1
    assert data['picture'] == 'picture file'
    assert data['num_test'] == 0
    assert isinstance(datetime.strptime(data['register_date'], "%Y-%m-%d %H:%M:%S"), datetime)


def test_user_get_no_result_found():
    response = app.test_client().get(
        '/user/10',
        content_type='application/json',
        headers={"Authorization": f"Bearer {encoded_admin}"}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['ERROR'] == f'Item not found 10'


def test_user_insert():
    response = app.test_client().post(
        '/user/',
        data=json.dumps({'name': 'insert_user', 'email': 'email.example.com', 'role': 2}),
        content_type='application/json',
        headers={"Authorization": f"Bearer {encoded_admin}"}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_201_CREATED
    assert data['name'] == 'insert_user'


def test_user_insert_sql_alchemy_error():
    response = app.test_client().post(
        '/user/',
        data=json.dumps({'name': 'insert_user', 'email': 'testuser@test.com', 'role': 15}),
        content_type='application/json',
        headers={"Authorization": f"Bearer {encoded_admin}"}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_user_insert_key_error():
    response = app.test_client().post(
        '/user/',
        data=json.dumps({'name': 'insert_user', 'role': 1}),
        content_type='application/json',
        headers={"Authorization": f"Bearer {encoded_admin}"}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data['ERROR'] == "Missing key 'email'"


def test_user_update():
    response = app.test_client().put(
        '/user/2',
        data=json.dumps({'role': 1}),
        content_type='application/json',
        headers={"Authorization": f"Bearer {encoded_admin}"}
    )
    data = json.loads(response.get_data(as_text=True))
    assert response.status_code == 202
    assert data['role'] == 1


def test_user_update_sql_alchemy_error():
    response = app.test_client().put(
        '/user/2',
        data=json.dumps({'role': None}),
        content_type='application/json',
        headers={"Authorization": f"Bearer {encoded_admin}"}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_user_update_key_error():
    response = app.test_client().put(
        '/user/2',
        data=json.dumps({'xpto': 1}),
        content_type='application/json',
        headers={"Authorization": f"Bearer {encoded_admin}"}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert data['ERROR'] == "Missing key 'role'"


def test_user_update_no_result_found():
    response = app.test_client().put(
        '/user/10',
        data=json.dumps({'role': 1}),
        content_type='application/json',
        headers={"Authorization": f"Bearer {encoded_admin}"}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert data['ERROR'] == f'Item not found 10'