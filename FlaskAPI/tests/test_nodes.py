from flask_api import status

from app import app
from flask import json
from tests.test_base import encoded_user, encoded_admin


def test_node_list_get():
    response = app.test_client().get(
        '/node'
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)

    assert response.status_code == status.HTTP_200_OK
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['name'] == 'APU_TEST'


def test_node_post():
    response = app.test_client().post(
        '/node',
        data=json.dumps({'name': 'inserted_node',
                         'ip': '192.168.1.150',
                         'port': 8000}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)

    assert response.status_code == status.HTTP_201_CREATED
    assert data['name'] == 'inserted_node'


def test_node_post_key_error():
    response = app.test_client().post(
        '/node',
        data=json.dumps({'name': 'inserted_node'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_node_post_repeated_item():
    response = app.test_client().post(
        '/node',
        data=json.dumps({'ip': '127.0.0.1',
                         'port': 5001,
                         'name': 'APU_TEST'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_node_id_get_no_connection():
    response = app.test_client().get(
        '/node/1',
        headers={'Authorization': f'Bearer {encoded_user}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_444_CONNECTION_CLOSED_WITHOUT_RESPONSE


def test_node_id_get_no_content():
    response = app.test_client().get(
        '/node/300',
        headers={'Authorization': f'Bearer {encoded_user}'}
    )
    app.logger.info(response)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_node_update():
    response = app.test_client().put(
        '/node/3',
        data=json.dumps({'name': 'new_inserted_node',
                         'ip': '192.168.1.150',
                         'port': 8000}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)

    assert response.status_code == status.HTTP_202_ACCEPTED
    assert data['name'] == 'new_inserted_node'


def test_node_update_repeated_item():
    response = app.test_client().put(
        '/node/3',
        data=json.dumps({'ip': '127.0.0.1', 'port': 5001, 'name': 'APU_TEST'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_node_delete():
    response = app.test_client().delete(
        '/node/2',
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_200_OK

    response = app.test_client().get(
        '/node/2',
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_profile_delete_no_content():
    response = app.test_client().delete(
        '/node/300',
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    app.logger.info(response)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_profile_post_access_point_no_content():
    response = app.test_client().post(
        '/node/300/accesspoint',
        data=json.dumps({'data': 'dummy-request'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    app.logger.info(response)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_profile_post_access_point_no_conection():
    response = app.test_client().post(
        '/node/1/accesspoint',
        data=json.dumps({'data': 'dummy-request'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    app.logger.info(response)
    assert response.status_code == status.HTTP_444_CONNECTION_CLOSED_WITHOUT_RESPONSE


def test_profile_get_interface_point_no_content():
    response = app.test_client().get(
        '/node/300/enps03/scan',
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    app.logger.info(response)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_profile_get_interface_point_no_conection():
    response = app.test_client().get(
        '/node/1/enps03/scan',
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    app.logger.info(response)
    assert response.status_code == status.HTTP_444_CONNECTION_CLOSED_WITHOUT_RESPONSE


def test_profile_post_interface_command_no_content():
    response = app.test_client().post(
        '/node/300/enps03/command',
        data=json.dumps({'data': 'dummy-request'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    app.logger.info(response)
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_profile_post_interface_command_no_conection():
    response = app.test_client().post(
        '/node/1/enps03/scan',
        data=json.dumps({'ip': 'dummy-request'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    app.logger.info(response)
    assert response.status_code == status.HTTP_444_CONNECTION_CLOSED_WITHOUT_RESPONSE


def test_profile_post_connect_key_error():
    response = app.test_client().post(
        '/node/1/enps03/connect',
        data=json.dumps({'ip': 'dummy-request'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    app.logger.info(response)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_profile_post_iperfsv3_key_error():
    response = app.test_client().post(
        '/node/1/enps03/iperfsv3',
        data=json.dumps({'ip': 'dummy-request'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    app.logger.info(response)
    assert response.status_code == status.HTTP_400_BAD_REQUEST


def test_profile_post_iperfclient_key_error():
    response = app.test_client().post(
        '/node/1/enps03/iperfclient',
        data=json.dumps({'ip': 'dummy-request'}),
        content_type='application/json',
        headers={'Authorization': f'Bearer {encoded_admin}'}
    )
    app.logger.info(response)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

