# -*- coding: utf-8 -*-
"""
Created on Thu Jun 23 14:26:24 2022

@author: Fabian Pedreros
"""

### Portafolio de inversión en Python ###
## Obtención del portafolio ##

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


risk_free_rate = 0.0125 # Aproximadamente la tasa de los bonos por 10 años 
#%%
# Obtención de los nombres de los archivos en una lista

files = [x for x in listdir(PATH) if isfile(join(PATH, x))]
tickers = [os.path.splitext(x)[0] for x in files]
tickers
tickers.sort()
len(tickers)

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
# Unir en un único df múltiples acciones por el nombre de la columna

def merge_df_by_column_name(col_name, sdate, edate, *tickers):
    # Will hold data for all dataframes with the same column name
    mult_df = pd.DataFrame()
    
    for x in tickers:
        df = get_stock_df_from_csv(x)
        mask = (df.index >= sdate) & (df.index <= edate)
        mult_df[x] = df.loc[mask][col_name]
        
    return mult_df

#%%
# Optimización Markowitz del portafolio

"""
Harry Markowitz proved that you could make what is called an efficient portfolio. That is a portfolio that optimizes return while also minimizing risk. We don't benefit from analyzing individual securities at the same rate as if we instead considered a portfolio of stocks.

We do this by creating portfolios with stocks that are not correlated. We want to calculate expected returns by analyzing the returns of each stock multiplied by its weight.

w1r1 + w2r2 = rp

The standard deviation of the portfolio is found this way. Sum multiple calculations starting by finding the product of the first securities weight squared times its standard deviation squared. The middle is 2 times the correlation coefficient between the stocks. 
And, finally add those to the weight squared times the standard deviation squared for the second security.

(w1d1 + w2d2)^2 = w1^2*d1^2 + 2w1d1w2d2 + w2^2 * d2^2

"""

# Trazar la frontera más eficiente
# Selección de un portafolio con acciones previamente estudidas, con los datos del rendimiento acumulado e Ishimoku
# Para el caso seleccioné algunas de sectores epecíficos.

port_list = ['PLUG', 'AMRC', 'GNRC',
'HCC', 'RFP', 'CF',
'IIPR', 'BRT', 'BRG',
'CDNA', 'ZYXI', 'ARWR',
'ATLC', 'KNSL', 'LPLA',
'ENPH', 'APPS', 'SEDG',
'RCMT', 'FCN', 'MHH',
'NEE', 'MSEX', 'EXC',
'TTGT', 'ROKU', 'IRDM',
'OAS', 'VTNR', 'EGY']

num_stocks = len(port_list)
print(num_stocks)

# Generar un df con los precios de cierre de todas las acciones seleccionadas

mult_df = merge_df_by_column_name('Close', S_DATE, E_DATE, *port_list)

#%%
# Generar un gráfico para los precios de las acciones

fig = px.line(mult_df, x = mult_df.index, y = mult_df.columns)
fig.update_layout(height=1000, width=1800, showlegend=True)
fig.update_xaxes(title="Date", rangeslider_visible=True)
fig.update_yaxes(title="Price")
plot(fig)

#%%
# Generar una tranformación del precio y gráficar

mult_df_t = np.log10(mult_df)

fig = px.line(mult_df_t, x = mult_df_t.index, y = mult_df_t.columns)
fig.update_layout(height=1000, width=1800, showlegend=True)
fig.update_xaxes(title="Date", rangeslider_visible=True)
fig.update_yaxes(title="Log10 Price")
plot(fig)

#%%
# Retornos medios para un año (252 días hábiles)

returns = np.log(mult_df / mult_df.shift(1))
mean_ret = returns.mean()*252
print(mean_ret)

#%%
# Cálculo de la correlación de las acciones
returns.corr()

# Gráfico de la correlación de las acciones
# Queremos un portafolio con baja correlación entre las acciones
import seaborn as sns
matriz_correlacion = returns.corr(method='spearman')
fig = sns.heatmap(matriz_correlacion, annot=False)
# fig.update_layout(height=1000, width=1800, showlegend=True)
plt.show()

#%%
# Generación de pesos aleatorios cuya suma es uno

weights = np.random.random(num_stocks)
weights /= np.sum(weights)  # weights = weights / np.sum(weights)
print('Weights: ', weights)
print('Total weight: ', np.sum(weights))

# Cálculo del retorno promedio anual con los pesos aleatorios
print(np.sum(weights * returns.mean()) * 252)

#%%
# Cálculo de la volatilidad
# Riesgo del portafolio con los pesos actuales

print(np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights))))

#%%
# Ejecución de una simulación de 10000 portafolios mediante una función

p_ret = [] # Retornos lista
p_vol = [] # Volatilidad lista
p_SR = [] # Sharpe Ratio lista
p_wt = [] # Pesos por portafolio lista


for x in range(10000):
    # Generar pesos aleatorios
    p_weights = np.random.random(num_stocks)
    p_weights /= np.sum(p_weights)
    
    # Calculo del retonrno según los pesos
    ret_1 = np.sum(p_weights * returns.mean()) * 252
    p_ret.append(ret_1)
    
    # Cálculo de la volatilidad
    vol_1 = np.sqrt(np.dot(p_weights.T, np.dot(returns.cov() * 252, p_weights)))
    p_vol.append(vol_1)
    
    # Cálculo del Sharpe ratio
    SR_1 = (ret_1 - risk_free_rate) / vol_1
    p_SR.append(SR_1)
    
    # Almacenar los pesos para cada portafolio
    p_wt.append(p_weights)
    
# Convertir a arreglos de Numpy
p_ret = np.array(p_ret)
p_vol = np.array(p_vol)
p_SR = np.array(p_SR)
p_wt = np.array(p_wt)

p_ret, p_vol, p_SR, p_wt

#%%
# Gráfica de los portafolios simulados o frontera más eficiente
ports = pd.DataFrame({'Returns': p_ret, 'Volatility': p_vol, })
ports.plot(x='Volatility', y = 'Returns', kind = 'scatter', figsize = (19,9))

#%%
# Sharpe ratio

"""
People want to maximize returns while avoiding as much risk as possible. 
William Sharpe created the Sharpe Ratio to find the portfolio that provides the best return for the lowest amount of risk.

As return increases so does the Sharpe Ratio, but as Standard Deviation increase the Sharpe Ration decreases.

"""
# Devuelve el indice para el Sharpe Ratio más alto
SR_idx = np.argmax(p_SR)

# Encuentra los pesos ideales para el portafolio en ese index
i = 0
while i < num_stocks:
    print("Stock : %s : %2.2f" % (port_list[i], (p_wt[SR_idx][i] * 100)))
    i += 1
    
# Encuentra la volatilidad de ese portafolio
print("\nVolatility :", p_vol[SR_idx] * 100)
      
# Encuentra el retorno de ese portafolio
print("Return :", p_ret[SR_idx] * 100)

# Se puede támbien tomar los porcenatjes menores a uno y acercarlos a uno, después calcular el portafolio.
# En situaciones en las que los porcentajes son menores a uno, lo que se puede hacer es acercarlos a uno o a una acción, o directamente desecharlos