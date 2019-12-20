#!/home/john/anaconda3/bin/python3


'''
https://stackoverflow.com/questions/10434599/get-the-data-received-in-a-flask-request
'''

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
    zip       = str(request.form.get('zip'))
    items     = main.main(zip)
    len_items = list(range(0,len(items) ))
    #return items
    return render_template('craig_list_local_items.html', len_items=len_items,items=items, zip=zip)
    #try:
    #    return str(request.form.get('zip'))
    #except Exception as e:
    #    return str(e)

if __name__ == "__main__":
    dir(app.run)
    app.run(host='0.0.0.0',port=5000)
