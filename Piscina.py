# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 20:08:24 2019

Provo a creare il DB piscina

@author: ddeen
"""

import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import pandas as pd
import datetime

# creo un'istanza per poi passarla come eridità
Base = declarative_base()


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
    
    
    
    
    