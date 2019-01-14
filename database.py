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

# creo un'istanza per poi passarla come eridità
Base = declarative_base()


#%% Tabelle
class Piscina(Base):
    '''
    Tabella con l'elenco degli allenamenti in piscina
    '''
    __tablename__ = 'piscina_allenamenti'

    id = Column(Integer, autoincrement=True) # id univoco dell'allenamento
    data = Column(Date, primary_key=True) # data dell'allenamento
    piscina_location = Column(String(255), nullable=False) # in quale piscina
    n_vasche = Column(Integer, nullable=False)
    
    
class PiscinaLocation(Base):
    '''
    Lista delle piscine
    '''
    __tablename__ = 'piscina_location'
    
    id = Column(Integer, autoincrement=True) 
    piscina_location = Column(String(255), primary_key=True)#, ForeignKey('piscina_allenamenti.piscina_location'))
    piscina_allenamenti = relationship(Piscina)


#%% MAIN
#if __name__ == '__main__':
engine = create_engine('mysql:///sport.db')

Base.metadata.create_all(engine)
