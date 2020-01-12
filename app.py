#!/usr/bin/env python3

"""
app.py - Main Flask application file

- This script is the WSGI form parser/validator.

- This script requires Flask to be installed.

- It expects to be passed:
    - zip  # from nginx html forms

- It sends all returnables to return flask's render_template

- Credit:
https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request

TBD: Add js input validation
"""



import os
import sys
import time
from numbers import Number

import flask
from flask import Flask
from flask import request
from flask import render_template

import main

app = Flask(__name__)
app.debug = True

@app.route('/forms/', methods=['POST', 'GET'])
def get_data():

    try:
        zip = int(request.form.get('zip'))
        #if isinstance(zip, Number) and len(str(zip)) == 5:
    except ValueError:
        return render_template('nota5digitzip.html')
    except Exception as e:
        print(e)
        flask.abort(500)
    else:
        if len(str(zip)) == 5:
            all_posts, all_links, city, state   = main.main(zip)
            len_items                           = list(range(0,len(all_posts)))
            return render_template('craig_list_local_items.html', zip = zip,
                city = city, state = state, all_posts = all_posts,
                len_items = len_items, all_links = all_links)
        else:
            return render_template('nota5digitzip.html')


if __name__ == "__main__":
    dir(app.run)
    app.run(host='0.0.0.0',port=5000)
