#!/usr/bin/env python

from subprocess import check_output
import flask
import os
import sqlite3
import random
import string
from flask import Flask,request, session, escape, redirect, jsonify

# create our little application
app = Flask(__name__)
app.debug=True

@app.route('/')
#insert everything here
def welcome():
    app.logger.debug("welcome function called")
    return flask.render_template("index.html")


app.secret_key = os.urandom(24)

if __name__ == "__main__":
	app.run(port=61008)	
