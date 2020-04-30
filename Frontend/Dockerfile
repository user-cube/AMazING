FROM python:3.6

RUN mkdir /code
WORKDIR /code

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt


COPY . .
CMD ["python", "manage.py", "runserver", "0.0.0.0:8005"]
#CMD ["gunicorn", "SwitchController.wsgi", "--bind", "0.0.0.0:8001"]
