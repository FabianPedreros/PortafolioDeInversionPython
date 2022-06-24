# -*- coding: utf-8 -*-
"""
Created on Sun Jun 19 21:44:17 2022

@author: Fabian Pedreros
"""

### Portafolio de inversión en Python ###
## Decarga o consulta de la información de acciones desde Yahoo Finance ##

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates # Requerido para estilizar fechas
#Necesario para cuando se trabaja en notebooks
#%matplotlib inline 

import datetime as dt # Usado para definir fechas y tiempo

import time

import yfinance as yf # Utilizado para descargar la información bursátil de Yahoo Finance
import os # Para trabajar con directorios y archivos en el sistema operativo
from os import listdir
from os.path import isfile, join

import cufflinks as cf #Libreria para la conexión de plotly con pandas
import plotly.express as px
import plotly.graph_objects as go

from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
init_notebook_mode(connected = True)

cf.go_offline()

from plotly.subplots import make_subplots

import warnings
warnings.simplefilter('ignore')

#%%
# Definción de variables
PATH = 'E:\Estudio\Análisis de datos\Proyectos\Portafolio de inversión en python\Wilshire/'

# Fechas de inicio y finalización por defecto
S_DATE = '2017-02-01'
E_DATE = '2022-06-19'
S_DATE_DT = pd.to_datetime(S_DATE)
E_DATE_DT = pd.to_datetime(E_DATE)

#%%
# Generación de una función para la obtención de los datos de columnas desde los CSV

def get_column_from_csv (file, col_name):
    try:
        df = pd.read_csv(file)
    except FileNotFoundError:
        print('Archivo no existe')
    else:
        return df[col_name]
    
#%%
# Obtener la información del indicativo de las acciones de un archivo CSV previamente creado con los tickers
tickers = get_column_from_csv('E:\Estudio\Análisis de datos\Proyectos\Portafolio de inversión en python\Wilshire-5000-stocks.csv', 'Ticker')

#%%
# Guardar los datos de las acciones en un CSV
# Creación de la función que genera un dataframe con el ticker y la fecha de inicio

def save_to_csv_from_yahoo(folder, ticker):
    stock = yf.Ticker(ticker)
    
    try:
        print('Obtener datos para: ', ticker)
        # Obtención de los datos historicos del precio de cierre
        df = stock.history(period='5y')
        
        # Espera de dos segundos
        time.sleep(2)
        
        # Remoción del punto para guardar el archivo CSV
        # Guardar os datos en un CSV
        # Guardado del archivo
        the_file = folder + ticker.replace('.','_')+'.csv'
        print(the_file, ' Guardado')
        df.to_csv(the_file)
    except Exception as ex:
        print('No se pudo obtener datos para: ', ticker)

#%%
# Descarga de toda la información de las acciones

for x in range (0, 3481):
    save_to_csv_from_yahoo(PATH, tickers[x])
    print('Terminado')