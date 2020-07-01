from flask_api import status
from _datetime import datetime, timedelta

from app import app
from flask import json
from tests.test_base import encoded_user, encoded_admin


def test_experience_list_get():
    response = app.test_client().get(
        '/experience',
        query_string={'content': 'TEST', 'userID': 1, 'date': datetime.now().strftime("%Y-%m-%d"),
                      'status': 'SCHEDULED'},
        headers={'Authorization': f'Bearer {encoded_user}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(data, list)
    assert len(data) == 2
    assert data[0]['name'] == 'TEST_ANTOHER_EXPERIENCE'
        #verify if sorting is working



def test_experience_list_get_no_date():
    response = app.test_client().get(
        '/experience',
        query_string={'begin_date': (datetime.now() + timedelta(0,200)).strftime("%Y-%m-%d"), 'end_date': (datetime.now() + timedelta(0,500)).strftime("%Y-%m-%d")},
        headers={'Authorization': f'Bearer {encoded_user}'}
    )
    data = json.loads(response.get_data(as_text=True))
    app.logger.info(data)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(data, list)
    assert len(data) == 0
