# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 20:05:07 2019
Funzioni per il login e logout

@author: ddeen
"""

from flask import Blueprint, request, session, flash, url_for, redirect

# Blueprint per andare online 
login_flask = Blueprint('login_flask', __name__, template_folder='templates')

@login_flask.route('/login', methods=['POST'])
def login():
    if request.form['password'] == 'elenabella22' and request.form['username'] == 'admin':
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return redirect(url_for('home')) # return alla pagina iniziale
    
@login_flask.route("/logout")
def logout():
    session['logged_in'] = False
    return redirect(url_for('home')) # return alla pagina iniziale

