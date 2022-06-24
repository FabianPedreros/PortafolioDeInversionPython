# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 15:00:26 2022

@author: Fabian Pedreros
"""
### Portafolio de inversión en Python ###
## Generación de los cálculos estadísticos de las acciones consultadas ##

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
# Obtener los datos de los CSV creados

def get_stock_df_from_csv(ticker):
    try:
        df = pd.read_csv(PATH + ticker + '.csv', index_col=0)
    except FileNotFoundError:
        print('El archivo no existe')
    else:
        return df
#%%
# Obtener un listado de los stocks que han sido descargados 

files = [x for x in listdir(PATH) if isfile(join(PATH, x))]
tickers = [os.path.splitext(x)[0] for x in files]

tickers.sort()
len(tickers)

#%%
# Añadir una columna con los retornos diarios: precio de cierre de un día dividido en el anterior menos uno.

def add_daily_return_to_df (df):
    df['daily_return'] = df['Close']/df['Close'].shift(1) - 1
    return df

#%%
# Añadir una columna con los retornos acumulados: acumulado del retorno diario para cada día

def add_cum_return_to_df (df):
    df['cum_return'] = (1 + df['daily_return']).cumprod() # cumprod()function is used when we want to compute the cumulative product of array elements over a given axis
    return df

#%%
# Añadir Bollinger bands
"""
Bollinger Bands plot 2 lines using a moving average and the standard deviation defines how far apart the lines are. They also are used to define if prices are to high or low. When bands tighten it is believed a sharp price move in some direction. 
Prices tend to bounce off of the bands which provides potential market actions.

A strong trend should be noted if the price moves outside the band. If prices go over the resistance line it is in overbought territory and if it breaks through support it is a sign of an oversold position.
"""
# Definición de la función para las Bollinger bands
def add_bollinger_bands(df):
    # Generación de la banda central (promedio movil) del precio de cierre con una ventana de 20 días
    df['middle_band'] = df['Close'].rolling(window = 20).mean()
    # Generación de la banda superior con dos veces la desviación estándar
    df['upper_band'] = df['middle_band'] + 2*df['Close'].rolling(window = 20).std()
    # Generación de la banda inferior con dos veces menos la desviación estándar
    df['lower_band'] = df['middle_band'] - 2*df['Close'].rolling(window = 20).std()
    return df

#%%%
# Añadir los datos Ichimoku al df

"""
The Ichimoku (One Look) is considered an all in one indicator. It provides information on momentum, support and resistance. It is made up of 5 lines. If you are a short term trader you create 1 minute or 6 hour. Long term traders focus on day or weekly data.

Conversion Line (Tenkan-sen) : Represents support, resistance and reversals. Used to measure short term trends.
Baseline (Kijun-sen) : Represents support, resistance and confirms trend changes. Allows you to evaluate the strength of medium term trends. Called the baseline because it lags the price.
Leading Span A (Senkou A) : Used to identify future areas of support and resistance
Leading Span B (Senkou B) : Other line used to identify suture support and resistance
Lagging Span (Chikou) : Shows possible support and resistance. It is used to confirm signals obtained from other lines.
Cloud (Kumo) : Space between Span A and B. Represents the divergence in price evolution.
Formulas

Lagging Span = Price shifted back 26 periods
Base Line = (Highest Value in period + Lowest value in period)/2 (26 Sessions)
Conversion Line = (Highest Value in period + Lowest value in period)/2 (9 Sessions)
Leading Span A = (Conversion Value + Base Value)/2
Leading Span B = (Period high + Period low)/2 (52 Sessions)

"""
def add_Ichimoku(df):
    # Conversion Line = (Highest Value in period + Lowest value in period)/2 (9 Sessions)
    hi_val = df['High'].rolling(window = 9).max()
    low_val = df['Low'].rolling(window = 9).min() 
    df['Conversion'] = (hi_val + low_val)/2
    
    # Base Line = (Highest Value in period + Lowest value in period)/2 (26 Sessions)
    hi_val2 = df['High'].rolling(window = 26).max()
    low_val2 = df['Low'].rolling(window = 26).min() 
    df['Baseline'] = (hi_val2 + low_val2)/2
    
    # Leading Span A = (Conversion Value + Base Value)/2
    df['SpanA'] = ((df['Conversion'] + df['Baseline'])/2)
    
    # Leading Span B = (Period high + Period low)/2 (52 Sessions)
    hi_val3 = df['High'].rolling(window = 52).max()
    low_val3 = df['Low'].rolling(window = 52).min() 
    df['SpanB'] = ((hi_val3 + low_val3)/2)
     
    # Lagging Span = Price shifted back 26 periods
    df['Lagging'] = df['Close'].shift(-26)
    
    return df
#%%
# Prueba de generación de cálculos para un archivo csv
try:
    print('Trabajando en:', 'A')
    new_df = get_stock_df_from_csv('A')
    new_df = add_daily_return_to_df(new_df)
    new_df = add_cum_return_to_df(new_df)
    new_df = add_bollinger_bands(new_df)
    new_df = add_Ichimoku(new_df)
    new_df.to_csv(PATH + 'A' + '.csv')
except Exception as ex:
    print(ex)
    

#%%
# Realizar y añadir los cálculos a todos los archivos de los tickers o acciones
for x in tickers :
    try:
        print('Trabajando en:', x)
        new_df = get_stock_df_from_csv(x)
        new_df = add_daily_return_to_df(new_df)
        new_df = add_cum_return_to_df(new_df)
        new_df = add_bollinger_bands(new_df)
        new_df = add_Ichimoku(new_df)
        new_df.to_csv(PATH + x + '.csv')
    except Exception as ex:
            print(ex)