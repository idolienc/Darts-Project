# Makes app available for all modules in the package
from flask import Flask

app = Flask(__name__)

from . import routes

app.secret_key = '123'