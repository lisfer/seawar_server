from flask import Flask
from flask_auto_docs import FlaskAutoDocs

app = Flask(__name__)
app.api_docs = FlaskAutoDocs(app)

app.secret_key = '<secret>'
app.config['TEMPLATES_AUTO_RELOAD'] = True


from .views import *
