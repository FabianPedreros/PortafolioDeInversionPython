# -*- coding: utf-8 -*-
"""
Created on Tue Jun 21 15:56:11 2022

@author: Fabian Pedreros
"""

### Portafolio de inversión en Python ###
## Generación de los gráficos para las acciones consultadas ##

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
# Gráficar las Bollinger bands

def plot_with_boll_bands(df, ticker):
    
    fig = go.Figure()

# Gráficar las velas con Plotly
    candle = go.Candlestick(x=df.index, open=df['Open'],
    high=df['High'], low=df['Low'],
    close=df['Close'], name="Candlestick")

# Gráficar las tres líneas calculadas
    upper_line = go.Scatter(x=df.index, y=df['upper_band'], 
    line=dict(color='rgba(250, 0, 0, 0.75)', 
    width=1), name="Upper Band")

    mid_line = go.Scatter(x=df.index, y=df['middle_band'], 
    line=dict(color='rgba(0, 0, 250, 0.75)', 
    width=0.7), name="Middle Band")

    lower_line = go.Scatter(x=df.index, y=df['lower_band'], 
    line=dict(color='rgba(0, 250, 0, 0.75)', 
    width=1), name="Lower Band")

# Agregar los cuatro gráficos en uno solo
    fig.add_trace(candle)
    fig.add_trace(upper_line)
    fig.add_trace(mid_line)
    fig.add_trace(lower_line)

# Dar titulos al gráfico y los ejes, así como adicionar un slider
    fig.update_xaxes(title="Date", rangeslider_visible=True)
    fig.update_yaxes(title="Price")
        
    fig.update_layout(title=ticker + " Bollinger Bands",
    height=1000, width=1800, showlegend=True)
    plot(fig)
    
#%%

# Función para la asignación del color de la nube

def get_fill_color(label):
    if label >= 1:
        return 'rgba(0,250,0,0.4)'
    else:
        return 'rgba(250,0,0,0.4)'

# Función para la gráfica de Ishimoku

def get_Ichimoku(df):

    candle = go.Candlestick(x=df.index, open=df['Open'],
    high=df['High'], low=df["Low"], close=df['Close'], name="Candlestick")

    df1 = df.copy()
    fig = go.Figure()
    df['label'] = np.where(df['SpanA'] > df['SpanB'], 1, 0)
    df['group'] = df['label'].ne(df['label'].shift()).cumsum()

    df = df.groupby('group')

    dfs = []
    for name, data in df:
        dfs.append(data)

    for df in dfs:
        fig.add_traces(go.Scatter(x=df.index, y=df.SpanA,
        line=dict(color='rgba(0,0,0,0)')))

        fig.add_traces(go.Scatter(x=df.index, y=df.SpanB,
        line=dict(color='rgba(0,0,0,0)'),
        fill='tonexty',
        fillcolor=get_fill_color(df['label'].iloc[0])))

    baseline = go.Scatter(x=df1.index, y=df1['Baseline'], 
    line=dict(color='pink', width=2), name="Baseline")

    conversion = go.Scatter(x=df1.index, y=df1['Conversion'], 
    line=dict(color='black', width=1), name="Conversion")

    lagging = go.Scatter(x=df1.index, y=df1['Lagging'], 
    line=dict(color='purple', width=2), name="Lagging")

    span_a = go.Scatter(x=df1.index, y=df1['SpanA'], 
    line=dict(color='green', width=2, dash='dot'), name="Span A")

    span_b = go.Scatter(x=df1.index, y=df1['SpanB'], 
    line=dict(color='red', width=1, dash='dot'), name="Span B")

    fig.add_trace(candle)
    fig.add_trace(baseline)
    fig.add_trace(conversion)
    fig.add_trace(lagging)
    fig.add_trace(span_a)
    fig.add_trace(span_b)
    
    fig.update_layout(height=1000, width=1800, showlegend=True)

    plot(fig)
    
#%%
# Prueba de gráfica para un stick específico
newdf = get_stock_df_from_csv('AA')
plot_with_boll_bands(newdf, 'AA')
get_Ichimoku(newdf)


