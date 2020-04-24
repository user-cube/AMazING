from __init__ import create_app

app = create_app('settings')

if __name__ == '__main__':

    app.run(host=app.config['HOST'],
            port=app.config['PORT'],
            debug=app.config['DEBUG'])
