# app.py
from flask import Flask

# Creates object app belonging to Flask class
app = Flask(__name__)

# When flask recieves this request, it will call the index function
@app.route('/')
def index():
    return "Hello, World!"