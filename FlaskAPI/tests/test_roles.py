from flask_api import status

from app import app
from flask import json
from tests.test_base import encoded_user, encoded_admin


def test_role_list_get():
    response = app.test_client().get(
        '/role',
        headers={'Authorization': f'Bearer {encoded_user}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['role_name'] == 'test_role'


def test_role_id_get():
    response = app.test_client().get(
        '/role/1'
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)

    assert response.status_code == status.HTTP_200_OK


def test_role_id_get_no_content():
    response = app.test_client().get(
        '/role/300'
    )

    app.logger.info(response)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_role_post():
    response = app.test_client().post(
        '/role',
        data=json.dumps({'name': 'inserted_role'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)

    assert response.status_code == status.HTTP_201_CREATED
    assert data['role_name'] == 'inserted_role'


def test_role_post_key_error():
    response = app.test_client().post(
        '/role',
        data=json.dumps({'no_name': 'inserted_role'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_role_post_repeated_name():
    response = app.test_client().post(
        '/role',
        data=json.dumps({'name': 'test_role'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_role_update():
    response = app.test_client().put(
        '/role/2',
        data=json.dumps({'name': 'new_inserted_role'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert data['role_name'] == 'new_inserted_role'


def test_role_update_key_error():
    response = app.test_client().put(
        '/role/2',
        data=json.dumps({'no_name': 'inserted_role'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_role_update_repeated_name():
    response = app.test_client().put(
        '/role/2',
        data=json.dumps({'name': 'test_role'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_profile_update_no_content():
    response = app.test_client().put(
        '/role/300',
        data=json.dumps({'name': 'inserted'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    app.logger.info(response)
    assert response.status_code == status.HTTP_204_NO_CONTENT



def test_role_delete():
    response = app.test_client().delete(
        '/role/2',
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_200_OK

    response = app.test_client().get(
        '/role/2',
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_profile_delete_no_content():
    response = app.test_client().delete(
        '/role/300',
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    app.logger.info(response)
    assert response.status_code == status.HTTP_204_NO_CONTENT


