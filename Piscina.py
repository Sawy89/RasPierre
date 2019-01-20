# -*- coding: utf-8 -*-
"""
Created on Sun Jan 13 20:08:24 2019

Provo a creare il DB piscina

@author: ddeen
"""

from sqlalchemy import Column, ForeignKey, Integer, String, Date, and_, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy import create_engine
import pandas as pd
import datetime
from dateutil.relativedelta import relativedelta
from highcharts import Highchart
from flask import Blueprint, render_template, url_for, request, redirect, flash , get_flashed_messages

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
    # Lista delle piscine
    session = DBSession()
    piscina = session.query(PiscinaLocation)
    piscina = session.query(PiscinaLocation, func.count(PiscinaAllenamento.id).label('Nallenamenti')
                            ).outerjoin(PiscinaAllenamento).group_by(PiscinaLocation.nome).all()
    
    # Creo delle date di default
    start_date_def1 = (datetime.datetime.now()-relativedelta(years=1)).replace(day=1).strftime('%Y-%m-%d') # l'ultimo anno
    start_date_def2 = (datetime.datetime.now()-datetime.timedelta(days=10)).replace(day=1).strftime('%Y-%m-%d') # l'ultimo mese
    stop_date_def = (datetime.datetime.now()+datetime.timedelta(days=1)).strftime('%Y-%m-%d') # domani
    
    return render_template('piscina_main.html', piscina=piscina, 
                           start_date_def1=start_date_def1, start_date_def2=start_date_def2, stop_date_def=stop_date_def)


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

    # Scarico i dati da DB: allenamenti compresi tra le date specificate
    session = DBSession()
    allen = session.query(PiscinaAllenamento).filter(and_(
            PiscinaAllenamento.data>=datetime.datetime.strptime(start_date,'%Y-%m-%d'), 
            PiscinaAllenamento.data<datetime.datetime.strptime(stop_date,'%Y-%m-%d')))
    session.close()
    
    return render_template('piscina_print.html', allen=allen, start_date=start_date, stop_date=stop_date)


@piscina_flask.route('/allenamenti/stat')
def piscinaStat():
    '''
    Pagina con le statistiche degli allenamenti nel periodo selezionato
    '''
    # input GET
    if request.method == 'GET':
        start_date = request.args.get('start_date', '')
        stop_date = request.args.get('stop_date', '')
    
    # Scarico i dati da DB: allenamenti compresi tra le date specificate
    query_text = ("""SELECT strftime('%Y',data) AS anno
                 , strftime('%m',data) AS mese
                 , count(0) AS Nvolte
                 , sum(n_vasche * 25 / lung_vasche) AS somma_vasche
                 , round(avg(n_vasche * 25 / lung_vasche), 1) AS media_vasche
                 , sum(n_vasche * lung_vasche) AS somma_metri
                 , round(avg(n_vasche * lung_vasche), 0) AS media_metri
            FROM piscina_allenamenti
            JOIN nome_piscina
                ON piscina_allenamenti.id_nome_piscina = nome_piscina.id
            WHERE data >= date('"""+start_date+"""')
                AND data < date('"""+stop_date+"""')
            GROUP BY
              anno
            , mese""")
    dati = pd.read_sql_query(query_text, engine)
    dati['media_metri'] = dati['media_metri'].astype('int')
    
    # Grafico
    chart = Highchart(width = 600, height = 500)
    dff=[]
    for i in range(len(dati)):
        dff.append(str(dati.anno[i])+'/'+str(dati.mese[i]))
    chart.set_options('xAxis', {'categories': dff, 'gridLineWidth': 1})
    chart.set_options('tooltip', {'formatter': 'default_tooltip'})
    chart.set_options('title', {'text': 'Statistiche mensili allenamenti'})
    chart.add_data_set(dati.Nvolte.values.tolist(), series_type='bar', name='Numero allenamenti')
    chart.add_data_set(dati.media_metri.values.tolist(), series_type='line', name='Media metri')
    chart.add_data_set(dati.somma_metri.values.tolist(), series_type='bar', name='Somma metri')
    chart.htmlcontent;
    
    return render_template('piscina_stat.html', start_date=start_date, stop_date=stop_date, 
                           df1=dati.to_html(classes='table',index=False,escape=True).replace('<th>','<th style = "background-color: #000099"	>'), 
                               fig1_head=chart.htmlheader, fig1_body=chart.content)


@piscina_flask.route('/allenamenti/insert/<int:piscina_id>', methods=['GET', 'POST'])
def piscinaInsert(piscina_id):
    '''
    Form per inserire un nuovo allenamento nella piscina selezionata
    '''
    # Scarico la piscina selezionata
    session = DBSession()
    piscina1 = session.query(PiscinaLocation).filter_by(id=piscina_id).one()
    
    if request.method == 'POST':
        # INSERIMENTO ALLENAMENTO
        # Leggo gli input
        allen_date = datetime.datetime.strptime(request.form['allen_date'],'%Y-%m-%d').date()
        n_vasche = int(request.form['n_vasche'])
        # creo oggetto allenamento
        a = PiscinaAllenamento(data=allen_date, id_nome_piscina=piscina_id, n_vasche=n_vasche)
        # carico
        session.add(a)
        session.commit()
        session.close()
        flash("Inserito nuovo allenamento!")
        return redirect(url_for('account_api.piscinaMain')) # return alla pagina iniziale
    else:
        # PAGINA DI INSERIMENTO
        return render_template('piscina_insert.html', piscina1=piscina1)


@piscina_flask.route('/allenamenti/delete/<int:allen_id>', methods=['GET', 'POST'])
#@piscina_flask.route('/allenamenti/delete', methods=['GET', 'POST'])
#@piscina_flask.route('/allenamenti/delete?allen_id=195<int:allen_id>', methods=['GET', 'POST'])
def piscinaDelete(allen_id):
    '''
    Pagina per cancellare un allenamento inserito
    '''
    # Scarico l'allenamento selezionato
    session = DBSession()
    allen1 = session.query(PiscinaAllenamento).filter_by(id=allen_id).one()
    
    if request.method == 'POST':
        # CANCELLAMENTO ALLENAMENTO
        # cancello l'elemento
        session.delete(allen1)
        session.commit()
        session.close()
        flash("Eliminato allenamento!")
        return redirect(url_for('account_api.piscinaMain'))
    else:
        # PAGINA DI CANCELLAMENTO
        return render_template('piscina_delete.html', allen1=allen1)
    

@piscina_flask.route('/insert', methods=['GET', 'POST'])
def piscinaNomeInsert():
    '''
    Form per inserire una nuova piscina
    '''
    if request.method == 'POST':
        # INSERIMENTO PISCINA
        session = DBSession()
        # Leggo gli input
        nome = request.form['nome']
        lung_vasche = int(request.form['lung_vasche'])
        # creo oggetto allenamento
        p1 = PiscinaLocation(nome=nome, lung_vasche=lung_vasche)
        # carico
        session.add(p1)
        session.commit()
        session.close()
        flash("Inserito nuova piscina!")
        return redirect(url_for('account_api.piscinaMain')) # return alla pagina iniziale
    else:
        # PAGINA DI INSERIMENTO
        return render_template('piscina_nome_insert.html') 


@piscina_flask.route('/delete/<int:id_nome_piscina>', methods=['POST'])
def piscinaNomeDelete(id_nome_piscina):
    '''
    Form per cancellare una piscina
    '''
    if request.method == 'POST':
        # CANCELLO PISCINA
        session = DBSession()
        # cercao oggetto piscina da eliminare
        p1 = session.query(PiscinaLocation).filter_by(id=id_nome_piscina).one()
        # carico
        session.delete(p1)
        session.commit()
        session.close()
        flash("Cancellata piscina!")
        return redirect(url_for('account_api.piscinaMain')) # return alla pagina iniziale

