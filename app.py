#!/home/john/anaconda3/bin/python3


'''
https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
'''

import os
import sys
import time
import pickle

import flask
from flask import Flask
from flask import request
from flask import render_template

import main

app = Flask(__name__)
app.debug = True


@app.route('/')
def hi():
    return "hi"

@app.route('/forms/', methods=['POST', 'GET'])
def get_data():
    try:
        zip                      = str(request.form.get('zip'))
        items, city, state,      = main.main(zip)
        len_items                = list( range(0,len(items)) )
        return render_template('craig_list_local_items.html', \
            len_items=len_items,items=items, zip=zip, city=city, state=state)
    except Exception as e:
        flask.abort(500)
        #return a default here()

if __name__ == "__main__":
    dir(app.run)
    app.run(host='0.0.0.0',port=5000)
