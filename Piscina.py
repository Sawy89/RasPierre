# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 20:08:24 2019

Provo a creare il DB piscina

@author: ddeen
"""

import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta

from flask import Blueprint, render_template, url_for, request

# creo un'istanza per poi passarla come eridità
Base = declarative_base()

# Create engine
engine = create_engine('sqlite:///sport.db')
Base.metadata.create_all(engine)
# Bind Base to engine
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


#%% Tabelle
class PiscinaLocation(Base):
    '''
    Lista delle piscine
    '''
    __tablename__ = 'nome_piscina'
    
    id = Column(Integer, primary_key=True) 
    nome = Column(String(255), unique=True)
    lung_vasche = Column(Integer, nullable=False) # lunghezza in metri delle vasche


class PiscinaAllenamento(Base):
    '''
    Tabella con l'elenco degli allenamenti in piscina
    '''
    __tablename__ = 'piscina_allenamenti'

    id = Column(Integer, primary_key=True) # id univoco dell'allenamento
    data = Column(Date, nullable=False) # data dell'allenamento
    id_nome_piscina = Column(Integer, ForeignKey('nome_piscina.id')) # in quale piscina
    n_vasche = Column(Integer)
    nome_piscina = relationship(PiscinaLocation)
    

#%% Carico le tabelle con i dati di un excel
def restoreNomePiscina(session):
    '''
    Ricarica l'elenco delle piscine
    '''
    # Piscina di saluzzo
    p1 = PiscinaLocation(nome='Saluzzo', lung_vasche=25)
    session.add(p1)
    session.commit()
    
    # Piscina di Casa
    p2 = PiscinaLocation(nome='Casa Carrù', lung_vasche=10)
    session.add(p2)
    session.commit()
    


def restorePiscinaAllenamenti(filename, session):
    '''
    funzione che legge il file contenete i vecchi dati sugli allenamenti in piscina
    e li ricarica su DB
    '''
    # Estraggo la lista delle piscine già caricate su DB
    piscine = session.query(PiscinaLocation)
    lista_piscine = [i.nome for i in piscine]
    
    # Leggo il file
    dati = pd.read_csv(filename, delimiter=';')
    
    # Carico il file
    for row_id in dati.index:
        nome_cur = dati.loc[row_id, 'nome_piscina'] # nome della piscina
        if nome_cur not in lista_piscine:
            # se non c'è, carico la piscina (con lung_vasche=25)
            p1 = PiscinaLocation(nome=nome_cur, lung_vasche=25)
            session.add(p1)
            session.commit()
            
            # riscarico la lista delle piscine
            print('!!! Caricata la piscina '+nome_cur+' (non presente) con vasca da 25m')
            piscine = session.query(PiscinaLocation)
            lista_piscine = [i.nome for i in piscine]
        
        # estraggo l'oggetto piscina
        p = piscine[lista_piscine.index(nome_cur)]
        
        # creo oggetto allenamento
        a = PiscinaAllenamento(data=datetime.datetime.strptime(dati.loc[row_id, 'data'],'%d/%m/%Y').date(), 
                                                               nome_piscina=p, 
                                                               n_vasche=int(dati.loc[row_id, 'n_vasche']))
        
        # carico
        session.add(a)
        session.commit()


#%% SITO

# Blueprint per andare online
piscina_flask = Blueprint('account_api', __name__, template_folder='templates_piscina')

@piscina_flask.route('/')
def piscinaMain():
    '''
    pagina principale della piscina
    '''
    # Creo delle date di default
    start_date_def = (datetime.datetime.now()-relativedelta(years=1)).strftime('%Y-%m-%d')
    stop_date_def = (datetime.datetime.now()+datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    
    return render_template('piscina_main.html', start_date_def=start_date_def, stop_date_def=stop_date_def)


#@piscina_flask.route('/allenamenti/<date:start_date>to<date:stop_date>/print')
@piscina_flask.route('/allenamenti/print')
def piscinaPrint():
    '''
    Pagina con l'elenco degli allenamenti nel periodo selezionato
    '''
    # input GET
#    start_date = request.form['start_date'] # per i POD devo usare questi
#    stop_date = request.form['stop_date']
    if request.method == 'GET':
        start_date = request.args.get('start_date', '')
        stop_date = request.args.get('stop_date', '')

    # Scarico i dati da DB
    session = DBSession()
    allen = session.query(PiscinaAllenamento).filter(and_(
            PiscinaAllenamento.data>=datetime.datetime.strptime(start_date,'%Y-%m-%d'), 
            PiscinaAllenamento.data<datetime.datetime.strptime(stop_date,'%Y-%m-%d')))
    session.close()
    
    return render_template('piscina_print.html', allen=allen, start_date=start_date, stop_date=stop_date)

    