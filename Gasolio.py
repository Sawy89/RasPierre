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
from flask import Blueprint, render_template, url_for, request, redirect, flash , get_flashed_messages, session
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
class Vettura(Base):
    '''
    Lista delle Automobili
    '''
    __tablename__ = 'vettura'
    
    id = Column(Integer, primary_key=True)
    auto = Column(String(255), nullable=False)
    tipo_carburante = Column(String(255), nullable=False)
    insertdate = Column(DateTime)


class Rifornimenti(Base):
    '''
    Lista delle piscine
    '''
    __tablename__ = 'rifornimenti'
    
    id = Column(Integer, primary_key=True) 
    data = Column(Date, nullable=False)
    auto = Column(String(255), ForeignKey('vettura.auto'))
    vettura = relationship(Vettura)
    distributore = Column(String(255))
    litri = Column(DECIMAL(6,2), nullable=False)
    prezzo = Column(DECIMAL(6,2), nullable=False)
    chilometri = Column(Integer, nullable=False)
    insertdate = Column(DateTime)


def calcoloConsumo():
    '''
    Funzione che calcola il consumo per tutti i dati presenti su DB
    e salva i risultati su DB
    '''
    dati_all = pd.DataFrame()
    
    # Lista delle vetture
    lista_vetture = pd.read_sql('SELECT auto FROM Vettura', engine)
    
    # Ciclo su tutte le vetture
    for auto_val in lista_vetture['auto']:
        # Scarico tutti i dati
        dati = pd.read_sql("SELECT * FROM rifornimenti WHERE auto = '"+auto_val+"' ", engine)
        
        # Euro al litro
        dati['euro_al_litro'] = round(dati['prezzo'] / dati['litri'],2)
        
        # Consumo singolo
        dati['chilometri_last'] = dati['chilometri'].shift(1).fillna(0)
        dati['chilometri_delta'] = dati['chilometri']-dati['chilometri_last']
        dati['consumo_al_litro'] = round(dati['chilometri_delta'] / dati['litri'], 2) # chilometri al litro
        dati['consumo_100km'] = round(100 * dati['litri'] / dati['chilometri_delta'], 2) # litri / 100km
        
        # Consumo cumulato
        dati['consumo_al_litro_cum'] = round(dati['chilometri_delta'].cumsum() / dati['litri'].cumsum(), 2)
        dati['consumo_100km_cum'] = round(100 * dati['litri'].cumsum() / dati['chilometri_delta'].cumsum(), 2)
        
        # Consumo legato al distributore (il distributore influisce sul consumo successivo)
        dati['consumo_al_litro_distributore'] = dati['consumo_al_litro'].shift(-1)
        dati['consumo_100km_distributore'] = dati['consumo_100km'].shift(-1)
        
        # Concateno tutte le vetture
        if dati_all.empty == True:
            dati_all = dati
        else:
            dati_all = dati_all.append(dati)
    
    return dati_all
    
#%% SITO

# Blueprint per andare online 
gas_flask = Blueprint('gas_flask', __name__, template_folder='templates_gasolio')

@gas_flask.route('/')
@loginRequired
def gasMain():
    '''
    pagina principale ai rifornimenti di gasolio
    '''
    # Lista delle vetture
    sessione_db = DBSession()
    dati = sessione_db.query(Vettura, func.count(Rifornimenti.id).label('Nrif')
                            ).outerjoin(Rifornimenti).group_by(Vettura.auto).all()
    
    # Calcolo consumo e lo salvo
    if 'df_all' not in session:
        session['df_all'] = calcoloConsumo()
    
    # Creo delle date di default
    start_date_def1 = (datetime.datetime.now()-relativedelta(years=1)).replace(day=1).strftime('%Y-%m-%d') # l'ultimo anno
    start_date_def2 = (datetime.datetime.now()-datetime.timedelta(days=15)).replace(day=1).strftime('%Y-%m-%d') # l'ultimo mese
    stop_date_def = (datetime.datetime.now()+datetime.timedelta(days=1)).strftime('%Y-%m-%d') # domani
    
    return render_template('gas_main.html', dati=dati, 
                           start_date_def1=start_date_def1, start_date_def2=start_date_def2, stop_date_def=stop_date_def)


@gas_flask.route('/rif/print')
@loginRequired
def rifPrint():
    '''
    Pagina con l'elenco dei rifornimenti nel periodo selezionato
    '''
    # input GET
    if request.method == 'GET':
        start_date = request.args.get('start_date', '')
        stop_date = request.args.get('stop_date', '')
    
    # Estraggo i dati per il periodo di interesse
    df_all = session['df_all']
    df_tmp = df_all.loc[].copy()
    
    
    return render_template('gas_print.html', df_all=df_tmp, start_date=start_date, stop_date=stop_date)


@gas_flask.route('/rif/stat')
@loginRequired
def stat():
    '''
    Pagina con le statistiche nel periodo selezionato
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


@gas_flask.route('/rif/insert/<int:piscina_id>', methods=['GET', 'POST'])
@loginRequired
def piscinaInsert(piscina_id):
    '''
    Form per inserire un nuovo allenamento nella piscina selezionata
    '''
    # Scarico la piscina selezionata
    sessione_db = DBSession()
    piscina1 = sessione_db.query(PiscinaLocation).filter_by(id=piscina_id).one()
    
    if request.method == 'POST':
        # INSERIMENTO ALLENAMENTO
        # Leggo gli input
        allen_date = datetime.datetime.strptime(request.form['allen_date'],'%Y-%m-%d').date()
        n_vasche = int(request.form['n_vasche'])
        # creo oggetto allenamento
        a = PiscinaAllenamento(data=allen_date, id_nome_piscina=piscina_id, n_vasche=n_vasche, insertdate=datetime.datetime.now())
        # carico
        sessione_db.add(a)
        sessione_db.commit()
        sessione_db.close()
        flash("Inserito nuovo allenamento!")
        return redirect(url_for('piscina_flask.piscinaMain')) # return alla pagina iniziale
    else:
        # PAGINA DI INSERIMENTO
        return render_template('piscina_insert.html', piscina1=piscina1, datanow=datetime.datetime.now())


@piscina_flask.route('/allenamenti/delete/<int:allen_id>', methods=['GET', 'POST'])
@loginRequired
def piscinaDelete(allen_id):
    '''
    Pagina per cancellare un allenamento inserito
    '''
    # Scarico l'allenamento selezionato
    sessione_db = DBSession()
    allen1 = sessione_db.query(PiscinaAllenamento).filter_by(id=allen_id).one()
    
    if request.method == 'POST':
        # CANCELLAMENTO ALLENAMENTO
        # cancello l'elemento
        sessione_db.delete(allen1)
        sessione_db.commit()
        sessione_db.close()
        flash("Eliminato allenamento!")
        return redirect(url_for('piscina_flask.piscinaMain'))
    else:
        # PAGINA DI CANCELLAMENTO
        return render_template('piscina_delete.html', allen1=allen1)
    

@piscina_flask.route('/insert', methods=['GET', 'POST'])
@loginRequired
def piscinaNomeInsert():
    '''
    Form per inserire una nuova piscina
    '''
    if request.method == 'POST':
        # INSERIMENTO PISCINA
        sessione_db = DBSession()
        # Leggo gli input
        nome = request.form['nome']
        lung_vasche = int(request.form['lung_vasche'])
        # creo oggetto allenamento
        p1 = PiscinaLocation(nome=nome, lung_vasche=lung_vasche, insertdate=datetime.datetime.now())
        # carico
        sessione_db.add(p1)
        sessione_db.commit()
        sessione_db.close()
        flash("Inserito nuova piscina!")
        return redirect(url_for('piscina_flask.piscinaMain')) # return alla pagina iniziale
    else:
        # PAGINA DI INSERIMENTO
        return render_template('piscina_nome_insert.html') 


@piscina_flask.route('/delete/<int:id_nome_piscina>', methods=['POST'])
@loginRequired
def piscinaNomeDelete(id_nome_piscina):
    '''
    Form per cancellare una piscina
    '''
    if request.method == 'POST':
        # CANCELLO PISCINA
        sessione_db = DBSession()
        # cercao oggetto piscina da eliminare
        p1 = sessione_db.query(PiscinaLocation).filter_by(id=id_nome_piscina).one()
        # carico
        sessione_db.delete(p1)
        sessione_db.commit()
        sessione_db.close()
        flash("Cancellata piscina!")
        return redirect(url_for('piscina_flask.piscinaMain')) # return alla pagina iniziale