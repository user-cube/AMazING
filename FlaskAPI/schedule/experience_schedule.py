"""
import datetime
date_now = datetime.now() + timedelta(20)
experience_schedule_query = db.session.query(Experience) \
            .filter(Experience.begin_date >= date_now) \
            .order_by(Experience.begin_date.asc()) \
            .one()



def schedule_experience():




def startNode():
    apu_request = f'http://127.0.0.1:5001/test'
    try:
        response = requests.post(url=apu_request, json=file, timeout=2)
        results = jsonify(response.json())
        results.status_code = response.status_code
        return results
    except requests.exceptions.ConnectionError:
        results = jsonify({"ERROR": f"{}: not founded"})
        results.status_code = status.HTTP_444_CONNECTION_CLOSED_WITHOUT_RESPONSE
        return results



"""

