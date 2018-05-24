from flask import Flask


app = Flask(__name__)

app.secret_key = '<secret>'
app.config['TEMPLATES_AUTO_RELOAD'] = True


from .views import *
