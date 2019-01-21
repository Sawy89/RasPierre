# -*- coding: utf-8 -*-
"""
Created on Wed Jan 16 19:50:41 2019

@author: ddeen
"""

from sqlalchemy import create_engine
import Piscina
from Piscina import Base, PiscinaLocation, PiscinaAllenamento
from sqlalchemy.orm import sessionmaker
import datetime


#%% MAIN Piscina
#if __name__ == '__main__':

# Creo DB engine
engine = create_engine('sqlite:///sport.db')

# Creo il DB
Base.metadata.create_all(engine)

#%% Carico le tabelle con i dati di un excel
def restoreNomePiscina():
    '''
    Ricarica l'elenco delle piscine
    '''
    # Piscina di saluzzo
    sessione_db = DBSession()
    p1 = PiscinaLocation(nome='Saluzzo', lung_vasche=25)
    sessione_db.add(p1)
    sessione_db.commit()
    
    # Piscina di Casa
    p2 = PiscinaLocation(nome='Casa Carrù', lung_vasche=10)
    sessione_db.add(p2)
    sessione_db.commit()
    


def restorePiscinaAllenamenti(filename):
    '''
    funzione che legge il file contenete i vecchi dati sugli allenamenti in piscina
    e li ricarica su DB
    '''
    sessione_db = DBSession()
    
    # Estraggo la lista delle piscine già caricate su DB
    piscine = sessione_db.query(PiscinaLocation)
    lista_piscine = [i.nome for i in piscine]
    
    # Leggo il file
    dati = pd.read_csv(filename, delimiter=';')
    
    # Carico il file
    for row_id in dati.index:
        nome_cur = dati.loc[row_id, 'nome_piscina'] # nome della piscina
        if nome_cur not in lista_piscine:
            # se non c'è, carico la piscina (con lung_vasche=25)
            p1 = PiscinaLocation(nome=nome_cur, lung_vasche=25)
            sessione_db.add(p1)
            sessione_db.commit()
            
            # riscarico la lista delle piscine
            print('!!! Caricata la piscina '+nome_cur+' (non presente) con vasca da 25m')
            piscine = sessione_db.query(PiscinaLocation)
            lista_piscine = [i.nome for i in piscine]
        
        # estraggo l'oggetto piscina
        p = piscine[lista_piscine.index(nome_cur)]
        
        # creo oggetto allenamento
        a = PiscinaAllenamento(data=datetime.datetime.strptime(dati.loc[row_id, 'data'],'%d/%m/%Y').date(), 
                                                               nome_piscina=p, 
                                                               n_vasche=int(dati.loc[row_id, 'n_vasche']))
        
        # carico
        sessione_db.add(a)
        sessione_db.commit()



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