# Portafolio De Inversion en Python

## Objetivo
Generar por medio de Python código que permita la extracción de datos de inversión bursátil, la selección de un conjunto de activos y la creación de un portafolio de inversión.

![image](https://user-images.githubusercontent.com/32172901/175699866-5ede7a49-7729-4580-965e-24a7db59430f.png)

## Datos
Los datos que vamos a utilizar son los de activos bursátiles que se encuentran en Yahoo Finance.
Para este caso se trabajaran con el grupo de activos Wilshire 5000.

![image](https://user-images.githubusercontent.com/32172901/175699923-24382d3e-1a85-4084-b1ab-577780f636df.png)

### Wilshire 5000

Es un índice ponderado por la capitalización bursátil del valor de mercado de todas las acciones americanas negociadas activamente en Estados Unidos. El índice pretende medir el rendimiento de la mayoría de las empresas que cotizan en bolsa con sede en los Estados Unidos, con datos de precios fácilmente disponibles, (se excluyen las acciones del Bulletin Board/penny y las acciones de empresas extremadamente pequeñas).

# Generación del portafolio

Se presenta a continuación un resúmen de las principales funcionalidades del código, para tener acceso a los archivos utilizar este link 

## 1. Obtención de la información de las acciones. Archivo: Portafolio_inversion_descarga.py

Decarga o consulta de la información de acciones desde Yahoo Finance ##

    # Definción de variables
    PATH = 'E:\Estudio\Análisis de datos\Proyectos\Portafolio de inversión en python\Wilshire/'

    # Fechas de inicio y finalización por defecto
    S_DATE = '2017-02-01'
    E_DATE = '2022-06-19'
    S_DATE_DT = pd.to_datetime(S_DATE)
    E_DATE_DT = pd.to_datetime(E_DATE)


Generación de una función para la obtención de los datos de columnas desde los CSV

    def get_column_from_csv (file, col_name):
        try:
            df = pd.read_csv(file)
        except FileNotFoundError:
            print('Archivo no existe')
        else:
            return df[col_name]
    
Obtener la información del indicativo de las acciones de un archivo CSV previamente creado con los tickers

    tickers = get_column_from_csv('E:\Estudio\Análisis de datos\Proyectos\Portafolio de inversión en python\Wilshire-5000-stocks.csv', 'Ticker')

Guardar los datos de las acciones en un CSV

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

Descarga de toda la información de las acciones

    for x in range (0, 3481):
        save_to_csv_from_yahoo(PATH, tickers[x])
        print('Terminado')


### Resultado: 

Generación de archivos CSV con los datos consultados de los ticks  establecidos, no se descargan para la totalidad de 3481 acciones, dado que los ticks han cambiado debido a fusiones o eliminaciones de empresas.

![image](https://user-images.githubusercontent.com/32172901/175706254-51a6b9c4-3114-4128-a68d-85add8648636.png)

Los CSV contienen datos para cada una de las acciones de la fecha de lectura histórica (diaria), precio de abertura, precio máximo, precio mínimo,  precio de cierre, dividendos generados, stock y splite.

![image](https://user-images.githubusercontent.com/32172901/175706980-c64f344c-b253-4995-816d-62a6a0b8cb54.png)

## 2. Generación de cálculos requeridos para la creación de gráficos


Obtener un listado de los stocks que han sido descargados 

    files = [x for x in listdir(PATH) if isfile(join(PATH, x))]
    tickers = [os.path.splitext(x)[0] for x in files]

    tickers.sort()
    len(tickers)


Añadir una columna con los retornos diarios: precio de cierre de un día dividido en el anterior menos uno.

    def add_daily_return_to_df (df):
        df['daily_return'] = df['Close']/df['Close'].shift(1) - 1
        return df

Añadir una columna con los retornos acumulados: acumulado del retorno diario para cada día

    def add_cum_return_to_df (df):
        df['cum_return'] = (1 + df['daily_return']).cumprod() # cumprod()function is used when we want to compute the cumulative product of array elements over a given axis
        return df


Añadir Bollinger bands

Bollinger Bands plot 2 lines using a moving average and the standard deviation defines how far apart the lines are. They also are used to define if prices are to high or low. When bands tighten it is believed a sharp price move in some direction. 
Prices tend to bounce off of the bands which provides potential market actions.

A strong trend should be noted if the price moves outside the band. If prices go over the resistance line it is in overbought territory and if it breaks through support it is a sign of an oversold position.

Definición de la función para las Bollinger bands

    def add_bollinger_bands(df):
        # Generación de la banda central (promedio movil) del precio de cierre con una ventana de 20 días
        df['middle_band'] = df['Close'].rolling(window = 20).mean()
        # Generación de la banda superior con dos veces la desviación estándar
        df['upper_band'] = df['middle_band'] + 2*df['Close'].rolling(window = 20).std()
        # Generación de la banda inferior con dos veces menos la desviación estándar
        df['lower_band'] = df['middle_band'] - 2*df['Close'].rolling(window = 20).std()
        return df


Añadir los datos Ichimoku al df

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

Prueba de generación de cálculos para un archivo csv

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
    

Realizar y añadir los cálculos a todos los archivos de los tickers o acciones

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
### Resultado: 

Se obtiene para cada stock en cada archivo csv, los valores del retorno diario, retorno acumulado desde la fecha inicial, el promedio móvil, banda superior e inferior, línea base, Span A, Span B y lagging.

![image](https://user-images.githubusercontent.com/32172901/175719207-edef584c-43aa-436e-9c43-e8efd3f377da.png)

## 3. Generación de las funciones para la creación de las gráficas de Bollinger Bands e Ichimoku.

Gráficar las Bollinger bands

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

Gráfica de Ishimoku

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
        
 ### Resultado:
 
Gráfica de Bollinger Bands para el ticker AA.
 
![image](https://user-images.githubusercontent.com/32172901/175719988-5b4239a8-fdce-4a6e-b19e-37be9444d498.png)


Gráfica Ishimoku para el ticker AA.

![image](https://user-images.githubusercontent.com/32172901/175719907-bb833fde-9813-4356-bb5a-2959619edddc.png)

 

## 4. Obtener la información de los sectores para las acciones que conforman el Wilshire 5000.


Esta información se encuentra en el archivo 'big_stock_sectors.csv'

    sec_df = pd.read_csv('E:\Estudio\Análisis de datos\Proyectos\Portafolio de inversión en python/big_stock_sectors.csv')
    
![image](https://user-images.githubusercontent.com/32172901/175720425-5e6e3fac-771f-41aa-b665-22cc7eaef9b5.png)


Separación en diferentes df de las acciones por sector

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


Creación de función para el cálculo del retorno acumulado para cada una de las acciones

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

Aplicación de la función para encontrar el acumulado de las acciones

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

Revisión por sector de las acciones con mayor rendimiento acumulado

    print('Top 10 Industrial')
    print(Industrial.sort_values(by=['CUM_RET'], ascending=False).head(10))
    
![image](https://user-images.githubusercontent.com/32172901/175720576-a49aeb46-31a2-4f56-8e99-6e3e7472871b.png)

Acciones seleccionadas por mayor retorno acumulado: PLUG, AMRC, GNRC

Gráficar alguna de las acciones para decidir en cual se podría llegar a invertir.

    df_ind = get_stock_df_from_csv('AMRC')
    get_Ichimoku(df_ind)
    
![image](https://user-images.githubusercontent.com/32172901/175720654-4b980d82-cc5c-4ed7-803b-2cf54c643986.png)


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


 








