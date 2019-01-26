# -*- coding: utf-8 -*-
"""
Created on Tue Jan 22 20:12:49 2019

@author: ddeen
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
import pandas as pd

# leggo il file
filename = 'static/gasolio.csv'
dati = pd.read_csv(filename, delimiter=';')
dati['insertdate'] = datetime.datetime.now() # aggiungo insertdate
# converto la stringa in data
for i in dati.index:
    dati.loc[i,'data'] = datetime.datetime.strptime(dati.loc[i,'data'],'%d/%m/%Y').date()

# carico su DB
engine = create_engine('sqlite:///gasolio.db')
dati.to_sql('rifornimenti', engine, if_exists='append', index=False)

# creo il df e carico su DB la lista delle vetture
dati2 = pd.DataFrame([['Fiesta','diesel',datetime.datetime.now()]], columns=['auto','tipo_carburante','insertdate'])
dati2.to_sql('vettura', engine, if_exists='append', index=False)
