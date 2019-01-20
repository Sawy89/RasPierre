# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 21:15:54 2019

Contiene il Main del progetto RasPierre

@author: ddeen
"""

#from sqlalchemy import create_engine
#import Piscina
from Piscina import Base, piscina_flask
#from sqlalchemy.orm import sessionmaker
#from Piscina import *
from flask import Flask, flash, render_template, request, session
import os

app = Flask(__name__)
app.register_blueprint(piscina_flask, url_prefix='/piscina')


@app.route('/')
def home():
    if not session.get('logged_in'):
        return render_template('login.html')
    else:
        return render_template('index.html')
 
@app.route('/login', methods=['POST'])
def do_admin_login():
    if request.form['password'] == 'elenabella22' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()
    
@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()

 
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
#    app.debug = 5000
    app.run(debug=True,host='0.0.0.0', port=5000)