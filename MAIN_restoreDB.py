# -*- coding: utf-8 -*-
"""
Created on Wed Jan 16 19:50:41 2019

@author: ddeen
"""

from sqlalchemy import create_engine
import Piscina
from Piscina import Base
from sqlalchemy.orm import sessionmaker


#%% MAIN Piscina
#if __name__ == '__main__':

# Creo DB engine
engine = create_engine('sqlite:///sport.db')

# Creo il DB
Base.metadata.create_all(engine)

#%% Ricarico i vecchi dati

# Bind Base to engine
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

# open session
session = DBSession()

# Carico la lista delle piscine
#Piscina.restoreNomePiscina(session)

# Carico la lista degli allenamenti
filename = 'static/Piscina.csv'
Piscina.restorePiscinaAllenamenti(filename, session)



# %% prova query
import pandas as pd
query = 'SELECT * FROM piscina_allenamenti'
aaa = pd.read_sql(query, engine)

session.close()