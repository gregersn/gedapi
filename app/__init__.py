from flask import Flask

app = Flask(__name__)
app.config['GEDCOM'] = None

from app import routes
from app import gedcom
