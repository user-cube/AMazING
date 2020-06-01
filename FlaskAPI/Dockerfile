FROM python:3
ADD ./ /app
WORKDIR /app
RUN apt-get update
RUN python -m pip install --upgrade pip
RUN pip install -r requirements.txt
ENV TZ=Europe/Lisbon
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
CMD python app.py
