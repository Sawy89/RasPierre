# -*- coding: utf-8 -*-
"""
Created on Tue Jan 15 21:15:54 2019

Contiene il Main del progetto RasPierre

@author: ddeen
"""

from sqlalchemy import create_engine
import Piscina
from Piscina import Base
from sqlalchemy.orm import sessionmaker
from Piscina import *
from flask import Flask

# ??
SECRET_KEY = '42o108'

app = Flask(__name__)
app.register_blueprint(piscina_flask, url_prefix='/piscina')
app.secret_key = SECRET_KEY

@app.route('/')
@app.route('/hello')
def HelloWorld():
    return "Hello World"

if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0', port=5000)




#%% MAIN Piscina
#if __name__ == '__main__':

# Creo DB engine
#engine = create_engine('sqlite:///sport.db')

# Creo il DB
#Base.metadata.create_all(engine)
