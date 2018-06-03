from flask import Flask, g, session
from flask_auto_docs import FlaskAutoDocs


__version__ = '1.0.0'


app = Flask(__name__)
app.api_docs = FlaskAutoDocs(app)

app.secret_key = '<secret>'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['DEVELOP'] = True  #used for developing - frontend part developed on other local server


from .views import *


@app.after_request
def save_session(response):
    if g.get('to_session'):
        while g.to_session:
            name, obj = g.to_session.popitem()
            session[name] = obj.to_json()
    return response


if app.config['DEVELOP']:
    @app.after_request
    def add_cross_origin(response):
        response.headers['Access-Control-Allow-Origin'] = 'http://localhost:3000'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response
