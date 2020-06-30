# Frontend
AMazING frontend made in Django.

## Setup (locally)
```shell
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ python manage.py runserver
```

## Setup (docker)

```shell
$ docker pull ruicoelho43/frontendpi:latest
$ docker run -d -p 8005:8005 ruicoelho43/frontendpi:latest
```
