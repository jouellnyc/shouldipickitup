#!/home/john/anaconda3/bin/python3

"""
app.py - Main Flask application file

- This script is the WSGI form parser/validator.

- This script requires Flask to be installed.

- It expects to be passed:
    - zip # from nginx html form

- It sends all returnables to return flask's render_template

- Credit/Refs:
https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
https://stackoverflow.com/questions/12551526/cast-flask-form-value-to-int

TBD: - Add js input validation
     - Add cool look ahead form query
"""


import os
import sys
import time
import logging

import flask
from flask import Flask
from flask import request
from flask import render_template

import main

app = Flask(__name__)
app.debug = True

@app.route('/forms/', methods=['POST', 'GET'])
def get_data():
    """
    Return a view to Flask with relevant details

    zip comes in as a 'str' and most easily is tested by casting to 'int'
    and checking len(str(zip)) at loss of some duplicated logic/code.

    zip goes back to a 'str' to be queried by mongodb and printed in HTML
    """
    try:
        zip = request.form.get('zip')
        if len(str(zip)) == 5:
            try:
                if zip[0] == 0:
                    int(zip[1:])
                else:
                    int(zip)
            except ValueError:
                return render_template('nota5digitzip.html')
            else:
                zip = str(zip)
                all_posts, all_links, all_cust, city, state   = main.main(zip)
                len_items                                     = len(all_posts)
                return render_template('craig_list_local_items.html',
                    zip = zip, city = city, state = state, all_posts = all_posts,
                    len_items = len_items, all_links = all_links,
                    all_cust = all_cust)
        else:
             return render_template('nota5digitzip.html')
    except Exception as e:
        logging.exception("BUG")
        flask.abort(500)


if __name__ == "__main__":
    app.run(host='0.0.0.0',port=8000)
