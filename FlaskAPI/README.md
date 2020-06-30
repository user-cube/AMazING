# Install (locally)

```shell
$ python -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

To run:
```shell
$ python app.py
```

# Install (docker)

```shell
$ docker pull ruicoelho43/apipi:latest
$ docker run -d -p 5000:5000 ruicoelho43/apipi:latest
```
