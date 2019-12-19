#!/home/john/anaconda3/bin/python3

'''

https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request

'''

import os
import sys
import time
import pickle

from flask import Flask
from flask import request

app = Flask(__name__)
app.debug = True


@app.route('/')
def hi():
    return "hi"

@app.route('/forms/', methods=['POST', 'GET'])
def get_data():
        try:
            return str(request.form.get('zip'))
        except Exception as e:
            return str(e)

if __name__ == "__main__":
    dir(app.run)
    app.run(host='0.0.0.0',port=5000)
