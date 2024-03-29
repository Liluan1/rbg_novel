from app import create_app
from flask_script import Manager

app = create_app('default')
app.config['debug'] = True
manager = Manager(app)

if __name__ == '__main__':
    app.run()