# app.py

from flask import Flask           # import flask
app = Flask(__name__)             # create an app instance

@app.route("/<name>")              # at the end point /<name>
def hello_name(name):              # call method hello_name
    mydata = [1,2,3]
    return "Hello " + name + " " + str(mydata)  # which returns "hello + name

if __name__ == "__main__":        # on running python app.py
    app.run()                     # run the flask app
