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
        zip                                 = str(request.form.get('zip'))
        all_posts, all_links, city, state   = main.main(zip)
        len_items                           = list(range(0,len(all_posts)))
        return render_template('craig_list_local_items.html', zip = zip,
            city = city, state = state, all_posts = all_posts,
            len_items = len_items, all_links = all_links)
    except Exception as e:
        print(e)
        flask.abort(500)
        #return a default here()

if __name__ == "__main__":
    dir(app.run)
    app.run(host='0.0.0.0',port=5000)
