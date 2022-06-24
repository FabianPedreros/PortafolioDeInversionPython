# -*- coding: utf-8 -*-
"""
Created on Wed Jun 22 16:14:40 2022

@author: Fabian Pedreros
"""
### Portafolio de inversión en Python ###
## Obtención de los sectores para las acciones consultadas ##

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
    
# Obtener la información de los sectores para las acciones que conforman el Wilshire 5000
# Esta información se encuentra en el archivo 'big_stock_sectors.csv'

sec_df = pd.read_csv('E:\Estudio\Análisis de datos\Proyectos\Portafolio de inversión en python/big_stock_sectors.csv')

# Separación en diferentes df de las acciones por sector

# Consulta de los sectores
print(sec_df['Sector'].unique())

"""
['Healthcare' 'Materials' 'SPAC' 'Discretionary' 'Real Estate'
 'Industrial' 'Financials' 'Information Technology' 'Industrials'
 'Staples' 'Services' 'Utilities' 'Communication' 'Energy' nan]
"""

indus_df = sec_df.loc[sec_df['Sector'] == 'Industrial']
health_df = sec_df.loc[sec_df['Sector'] == 'Healthcare']
it_df = sec_df.loc[sec_df['Sector'] == 'Information Technology']
comm_df = sec_df.loc[sec_df['Sector'] == 'Communication']
staple_df = sec_df.loc[sec_df['Sector'] == 'Staples']
discretion_df = sec_df.loc[sec_df['Sector'] == 'Discretionary']
materials_df = sec_df.loc[sec_df['Sector'] == 'Materials']
spac_df = sec_df.loc[sec_df['Sector'] == 'SPAC']
real_estate_df = sec_df.loc[sec_df['Sector'] == 'Real Estate']
financials_df = sec_df.loc[sec_df['Sector'] == 'Financials']
industrials_df = sec_df.loc[sec_df['Sector'] == 'Industrials']
services_df = sec_df.loc[sec_df['Sector'] == 'Services']
utilities_df = sec_df.loc[sec_df['Sector'] == 'Utilities']
energy_df = sec_df.loc[sec_df['Sector'] == 'Energy']


#%%
# Creación de función para el cálculo del retorno acumulado para cada una de las acciones

def get_cum_ret_for_stocks(stock_df):
    tickers = []
    cum_rets = []

    for index, row in stock_df.iterrows():
        df = get_stock_df_from_csv(row['Ticker'])
        if df is None:
            pass
        else:
            tickers.append(row['Ticker'])
            cum = df['cum_return'].iloc[-1]
            cum_rets.append(cum)
    return pd.DataFrame({'Ticker':tickers, 'CUM_RET':cum_rets})

#%%
# Aplicación de la función apra encontrar el acumulado de las acciones
# Me generaba error con los archivos que no tenían datos, así que los borré.

Healthcare = get_cum_ret_for_stocks(health_df)
Materials = get_cum_ret_for_stocks(materials_df)
SPAC = get_cum_ret_for_stocks(spac_df)
Discretionary = get_cum_ret_for_stocks(discretion_df)
Real_Estate = get_cum_ret_for_stocks(real_estate_df)
Industrial = get_cum_ret_for_stocks(indus_df)
Financials = get_cum_ret_for_stocks(financials_df)
IT = get_cum_ret_for_stocks(it_df)
Industrials = get_cum_ret_for_stocks(industrials_df)
Staples = get_cum_ret_for_stocks(staple_df)
Services = get_cum_ret_for_stocks(services_df)
Utilities = get_cum_ret_for_stocks(utilities_df)
Communication = get_cum_ret_for_stocks(comm_df)
Energy = get_cum_ret_for_stocks(energy_df)

#%%
# Revisión por sector de las acciones con mayor rendimiento acumulado

print('Top 10 Industrial')
print(Industrial.sort_values(by=['CUM_RET'], ascending=False).head(10))

# Acciones seleccionadas por mayor retorno acumulado: PLUG, AMRC, GNRC

# Gráficar alguna de las acciones para decidir en cual se podría llegar a invertir.
df_ind = get_stock_df_from_csv('AMRC')
get_Ichimoku(df_ind)

###

print('Top 10 Materials')
print(Materials.sort_values(by=['CUM_RET'], ascending=False).head(10))

# Acciones seleccionadas por mayor retorno acumulado: HCC, RFP, CF

# Gráficar alguna de las acciones para decidir en cual se podría llegar a invertir.
df_mat = get_stock_df_from_csv('HCC')
get_Ichimoku(df_mat)

###

print('Top 10 Discretionary')
print(Discretionary.sort_values(by=['CUM_RET'], ascending=False).head(10))

# Acciones seleccionadas por mayor retorno acumulado: CELH, BOOT, VERU

# Gráficar alguna de las acciones para decidir en cual se podría llegar a invertir.
df_Discretionary = get_stock_df_from_csv('CELH')
get_Ichimoku(df_Discretionary)


###

print('Top 10 Real_Estate')
print(Real_Estate.sort_values(by=['CUM_RET'], ascending=False).head(10))

# Acciones seleccionadas por mayor retorno acumulado: IIPR, BRT, BRG

# Gráficar alguna de las acciones para decidir en cual se podría llegar a invertir.
df_Real_Estate = get_stock_df_from_csv('IIPR')
get_Ichimoku(df_Real_Estate)


###

print('Top 10 Healthcare')
print(Healthcare.sort_values(by=['CUM_RET'], ascending=False).head(10))

# Acciones seleccionadas por mayor retorno acumulado: CDNA, ZYXI, ARWR

# Gráficar alguna de las acciones para decidir en cual se podría llegar a invertir.
df_Healthcare = get_stock_df_from_csv('ZYXI')
get_Ichimoku(df_Healthcare)

###

print('Top 10 Financials')
print(Financials.sort_values(by=['CUM_RET'], ascending=False).head(10))

# Acciones seleccionadas por mayor retorno acumulado: ATLC, KNSL, LPLA

# Gráficar alguna de las acciones para decidir en cual se podría llegar a invertir.
df_Financials = get_stock_df_from_csv('ATLC')
get_Ichimoku(df_Financials)

###

print('Top 10 IT')
print(IT.sort_values(by=['CUM_RET'], ascending=False).head(10))

# Acciones seleccionadas por mayor retorno acumulado: ENPH, APPS, SEDG

# Gráficar alguna de las acciones para decidir en cual se podría llegar a invertir.
df_IT = get_stock_df_from_csv('ENPH')
get_Ichimoku(df_IT)

###

print('Top 10 Industrials')
print(Industrials.sort_values(by=['CUM_RET'], ascending=False).head(10))

# Acciones seleccionadas por mayor retorno acumulado: CAR, BXC, PTSI

# Gráficar alguna de las acciones para decidir en cual se podría llegar a invertir.
df_Industrials = get_stock_df_from_csv('CAR')
get_Ichimoku(df_Industrials)

###

print('Top 10 Staples')
print(Staples.sort_values(by=['CUM_RET'], ascending=False).head(10))

# Acciones seleccionadas por mayor retorno acumulado: DAR, FRPT, SMPL

# Gráficar alguna de las acciones para decidir en cual se podría llegar a invertir.
df_Staples = get_stock_df_from_csv('DAR')
get_Ichimoku(df_Staples)

###

print('Top 10 Services')
print(Services.sort_values(by=['CUM_RET'], ascending=False).head(10))

# Acciones seleccionadas por mayor retorno acumulado: RCMT, FCN, MHH

# Gráficar alguna de las acciones para decidir en cual se podría llegar a invertir.
df_Services = get_stock_df_from_csv('RCMT')
get_Ichimoku(df_Services)

###

print('Top 10 Utilities')
print(Utilities.sort_values(by=['CUM_RET'], ascending=False).head(10))

# Acciones seleccionadas por mayor retorno acumulado: NEE, MSEX, EXC

# Gráficar alguna de las acciones para decidir en cual se podría llegar a invertir.
df_Utilities = get_stock_df_from_csv('NEE')
get_Ichimoku(df_Utilities)

###

print('Top 10 Communication')
print(Communication.sort_values(by=['CUM_RET'], ascending=False).head(10))

# Acciones seleccionadas por mayor retorno acumulado: TTGT, ROKU, IRDM

# Gráficar alguna de las acciones para decidir en cual se podría llegar a invertir.
df_Communication = get_stock_df_from_csv('TTGT')
get_Ichimoku(df_Communication)

###

print('Top 10 Energy')
print(Energy.sort_values(by=['CUM_RET'], ascending=False).head(10))

# Acciones seleccionadas por mayor retorno acumulado: OAS, VTNR, EGY

# Gráficar alguna de las acciones para decidir en cual se podría llegar a invertir.
df_Energy = get_stock_df_from_csv('OAS')
get_Ichimoku(df_Energy)





















