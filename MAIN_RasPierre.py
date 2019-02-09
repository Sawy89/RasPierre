# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 21:15:54 2019

Contiene il Main del progetto RasPierre

@author: ddeen
"""

from Piscina import piscina_flask
from Gasolio import gas_flask
from Login import login_flask, loginRequired

from flask import Flask, render_template
import os

app = Flask(__name__)
app.register_blueprint(piscina_flask, url_prefix='/piscina')
app.register_blueprint(gas_flask, url_prefix='/gas')
app.register_blueprint(login_flask, url_prefix='/auth')


@app.route('/')
@loginRequired
def home():
    return render_template('index.html')

 
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
#    app.debug = 5000
    app.run(debug=False,host='0.0.0.0', port=5000)