FROM python:3
ADD ./ /app
WORKDIR /app
RUN apt-get update
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
CMD python app.py
