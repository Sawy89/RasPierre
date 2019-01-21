# -*- coding: utf-8 -*-
"""
Created on Mon Jan 21 21:04:10 2019

App per tenere traccia dei rifornimenti di gasolio

@author: ddeen
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Date, and_, func, DateTime, DECIMAL 
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from highcharts import Highchart
from flask import Blueprint, render_template, url_for, request, redirect, flash , get_flashed_messages
from Login import loginRequired

# creo un'istanza per poi passarla come eridità
Base = declarative_base()

# Create engine
engine = create_engine('sqlite:///gasolio.db')
Base.metadata.create_all(engine)
# Bind Base to engine
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)


#%% Tabelle
class Rifornimenti(Base):
    '''
    Lista delle piscine
    '''
    __tablename__ = 'rifornimenti'
    
    id = Column(Integer, primary_key=True) 
    auto = Column(String(255), nullable=False)
    distributore = Column(String(255))
    litri = Column(DECIMAL(6,2), nullable=False)
    prezzo = Column(DECIMAL(6,2), nullable=False)
    chilometri = Column(Integer, nullable=False)

# Blueprint per andare online 
gasolio_flask = Blueprint('gasolio_flask', __name__, template_folder='templates_gasolio')


@gasolio_flask.route('/')
@loginRequired
def gasolioMain():
    '''
    pagina principale per i rifornimenti di gasolio
    '''
    # Lista delle piscine
    sessione_db = DBSession()
    piscina = sessione_db.query(PiscinaLocation)
    piscina = sessione_db.query(PiscinaLocation, func.count(PiscinaAllenamento.id).label('Nallenamenti')
                            ).outerjoin(PiscinaAllenamento).group_by(PiscinaLocation.nome).all()
    
    # Creo delle date di default
    start_date_def1 = (datetime.datetime.now()-relativedelta(years=1)).replace(day=1).strftime('%Y-%m-%d') # l'ultimo anno
    start_date_def2 = (datetime.datetime.now()-datetime.timedelta(days=10)).replace(day=1).strftime('%Y-%m-%d') # l'ultimo mese
    stop_date_def = (datetime.datetime.now()+datetime.timedelta(days=1)).strftime('%Y-%m-%d') # domani
    
    return render_template('piscina_main.html', piscina=piscina, 
                           start_date_def1=start_date_def1, start_date_def2=start_date_def2, stop_date_def=stop_date_def)