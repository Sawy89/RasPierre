# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 20:05:07 2019
Funzioni per il login e logout

@author: ddeen
"""

from flask import Blueprint, request, session, flash, url_for, redirect, render_template
from functools import wraps

# Blueprint per andare online 
login_flask = Blueprint('login_flask', __name__, template_folder='templates')


def loginRequired(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('You need to login first!')
            return redirect(url_for('login_flask.login'))
    return wrap


@login_flask.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        # Verifico LOGIN
        if request.form['password'] == 'elenabella22' and request.form['username'] == 'admin':
            session['logged_in'] = True
        else:
            flash('wrong password!')
        return redirect(url_for('home')) # return alla pagina iniziale
    elif request.method == 'GET':
        # Pagina inserimento login
        return render_template('login.html')

    
@login_flask.route("/logout")
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('home')) # return alla pagina iniziale
