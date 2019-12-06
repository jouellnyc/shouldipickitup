#!/home/john/anaconda3/bin/python3


import os
import sys
import time
import pickle

from flask import Flask
from flask import render_template

app = Flask(__name__)
app.debug = True

import  maintest

@app.route('/craigslist')
def get_data():
    data = maintest.main()
    return render_template('bootstrap_template.html', title='Home', data=data[0:3])

if __name__ == "__main__":
    dir(app.run)
    app.run(host='0.0.0.0',port=5000)
