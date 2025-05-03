# Makes app available for all modules in the package
from flask import Flask

app = Flask(__name__)

from . import routes

app.secret_key = 'eca17809-c94d-4963-a894-b8220b348f86'