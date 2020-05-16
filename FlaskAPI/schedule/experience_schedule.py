"""
date_now = datetime.now()
experience_schedule_query = db.session.query(Experience) \
            .filter(Experience.begin_date >= date_now) \
            .order_by(Experience.begin_date.asc()) \
            .one()



"""