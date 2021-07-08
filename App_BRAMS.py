from numpy import datetime64
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.graph_objs as go
import matplotlib.pyplot as plt
from bokeh.plotting import figure
from meteostat import Stations, Daily, Hourly, Monthly
import numpy as np
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.seasonal import seasonal_decompose
from dateutil.parser import parse


countries = ['Brasil','EUA']
intervals = ['Horária', 'Diária', 'Mensal']
cidades = ["Goiânia", "Fortaleza", "Natal", "Brasília"]

start_date = datetime.now()-timedelta(days=30)
end_date = datetime.now()

ende = datetime.now() - timedelta(days=365)
stop = datetime.now()


@st.cache
def consultar_dados_monthly(from_date, to_date):

    data = Monthly(83423, start = from_date, end = to_date)
    
    df = data.fetch() 
    
    result = seasonal_decompose(df["wspd"], model='additive', extrapolate_trend='freq', period= periodo)
    
    return(df, result)



@st.cache
def consultar_dados_daily(from_date, to_date):

    stations = Stations()

    stations = stations.nearby(-16.2333,  -48.9667 )

    station = stations.fetch()

    data = Daily(83423, start = from_date, end = to_date)
    df = data.fetch()
    periodo = int(len(df["wspd"])/2)
    result = seasonal_decompose(df["wspd"], model='additive', extrapolate_trend='freq', period= periodo)
    
    return(df, result)
# Função para formatar datas
def format_date(dt, format='%Y-%m-%d %H:%M:%S'):
    
    return dt.strftime(format)


def format_date_dia(dt, format='%d-%m'):
    
    return dt.strftime(format)

@st.cache
def excel_dados_diaria(data_excelI, data_excelF):
    
    mask = dft.loc[(pd.to_datetime(dft["TIMESTAMP"]) >= data_excelI) & (pd.to_datetime(dft["TIMESTAMP"]) <= data_excelF)] 
    #mask.set_index('TIMESTAMP', inplace=True)
  
    dto = mask.groupby(pd.to_datetime(mask["TIMESTAMP"]).dt.strftime('%j')).mean()

    dtd = mask.groupby(pd.to_datetime(mask["TIMESTAMP"]).dt.strftime('%j')).std()

    periodo = int(len(dto)/2)

    result = seasonal_decompose(dto["wnd_spd"], model='additive', extrapolate_trend='freq', period= periodo)

    return mask, dto, dtd, result

@st.cache
def excel_dados_mensal(data_excelI, data_excelF):
    
    mask = dft.loc[(pd.to_datetime(dft["TIMESTAMP"]) >= data_excelI) & (pd.to_datetime(dft["TIMESTAMP"]) <= data_excelF)] 
    
    dto = mask.groupby(pd.to_datetime(mask["TIMESTAMP"]).dt.strftime('%m')).mean()  
    
    dtd = mask.groupby(pd.to_datetime(mask["TIMESTAMP"]).dt.strftime('%m')).std()

    dt_max = mask.groupby(pd.to_datetime(mask["TIMESTAMP"]).dt.strftime('%m')).max()

    periodo = int(len(dto)/2)

    result = seasonal_decompose(dto["wnd_spd"], model='additive', extrapolate_trend='freq', period= periodo)

    return mask, dto, dtd, result

  



#CRIANDO UMA BARRA LATERAL
barra_lateral = st.sidebar.empty()

#Criando o radioBOX para escolher a fonte de dados
genre = st.sidebar.radio("Selecione a fonte de dados",('Excel', 'Meteostat'))

#Inicio da Parte do código que carrega os dados do EXCEL e plota os dados a partir das funções horaria, diária e mensal. 
if genre == 'Excel':
  
    uploaded_file = st.sidebar.file_uploader("Escolha o arquivo", type = ['csv', 'xlsx'])

    if uploaded_file is not None:

        try:
            dft = pd.read_excel(uploaded_file, index_col=None)
        except:
            dft = pd.read_excel(uploaded_file, index_col=None)

    dft = dft.drop(dft.index[0:3])

    dft.columns = ["TIMESTAMP", "wnd_spd", "rslt_wnd_spd", "wnd_dir_sonic", "std_wnd_dir", "wnd_dir_compass", "Ux_Avg",	"Uy_Avg",
                    "Uz_Avg", "u_star",	"Ux_stdev",	"Ux_Uy_cov", "Ux_Uz_cov", "Uy_stdev", "Uy_Uz_cov", "Uz_stdev"]
    
    dft = pd.DataFrame(dft)

    dft.ffill(inplace=True)

    date = list(dft["TIMESTAMP"])

    dateI = pd.to_datetime(date[0], format='%d-%m-%Y')
    dateF = pd.to_datetime(date[-1], format='%d-%m-%Y')

    interval_select = st.sidebar.selectbox("Análise:", intervals)
    data_excelI = st.sidebar.date_input('Data inicial:', dateI)
    data_excelF = st.sidebar.date_input('Data final:', dateF)   
    carregar_dados = st.sidebar.checkbox('Carregar dados') 

    st.title('Análise preliminar de sítio eólico') #elementos centrais da página

    st.write(dft)

    #dft = dft.rename(columns={'TIMESTAMP':'index'}).set_index('index')




    if data_excelI > data_excelF:
        st.sidebar.error('Data de ínicio maior do que data final')

    elif interval_select == "Diária":

        mask, dto, dtd, result = excel_dados_diaria(format_date(data_excelI), format_date(data_excelF))

       # data_f = sazonalidade_diaria(format_date(data_excelI), format_date(data_excelF))

        tempo = pd.to_datetime(mask["TIMESTAMP"], format="%d")

        try:
            
            x = mask['TIMESTAMP']
            # Criando o objeto do gráfico
            fig1 = go.Figure()

            # Funções 'add_trace' para criar as linhas do gráfico
            fig1.add_trace(go.Scatter(x=x, y=dft["wnd_spd"],
                                    mode='lines',
                                    name='Taxa de aparecimento do 1º sintoma'))
                                                    
            # Formatando o layout do gráfico
            fig1.update_layout(title='Série temporal completa',
                            xaxis_title='Data',
                            yaxis_title='Velocidade (m/s)',
                            width=900,
                            height=600)

            # Exibindo o elemento do gráfico na página                
            st.plotly_chart(fig1)

            """ Aqui são apresentados os valores de média diária"""	

            st.title("Tabela de Médias diária")
            st.write(dto)  


            x2 = dto.index
            # Criando o objeto do gráfico
            fig2 = go.Figure()

            # Funções 'add_trace' para criar as linhas do gráfico
            fig2.add_trace(go.Scatter(x=x2, y=dto["wnd_spd"],
                                    mode='lines',
                                    name='Média diária'))

            fig2.add_trace(go.Scatter(x=x2, y=result.seasonal,
                                    mode='lines',
                                    name='Sazonalidade Diária'))

            fig2.add_trace(go.Scatter(x=x2, y=result.trend,
                                    mode='lines',
                                    name='Tendência Diária'))  
                                                    
            # Formatando o layout do gráfico
            fig2.update_layout(title='Média diária para velocidade do vento',
                            xaxis_title='Dias',
                            yaxis_title='Velocidade (m/s)',
                            width=1000,
                            height=600)

            # Exibindo o elemento do gráfico na página                
            st.plotly_chart(fig2)

            """ Aqui são apresentados os valores de desvio Padrão diário"""

            st.title("Tabela de Desvio Padrão diário")
            st.write(dtd)  

            x3 = dtd.index
            # Criando o objeto do gráfico
            fig3 = go.Figure()

            # Funções 'add_trace' para criar as linhas do gráfico
            fig3.add_trace(go.Scatter(x=x3, y=dtd["wnd_spd"],
                                    mode='lines',
                                    name='Média diária'))
                                                    
            # Formatando o layout do gráfico
            fig3.update_layout(title='Média diária para velocidade do vento',
                            xaxis_title='Dias',
                            yaxis_title='Desvio Padrão',
                            width=1000,
                            height=600)

            # Exibindo o elemento do gráfico na página                
            st.plotly_chart(fig3)
            
            if carregar_dados:
                st.subheader('Dados')
                dados = st.dataframe(mask)
        except Exception as e:
            st.error(e)



    elif interval_select == "Mensal":

        mask, dto, dtd, result = excel_dados_mensal(format_date(data_excelI), format_date(data_excelF))

        tempo = pd.to_datetime(mask["TIMESTAMP"], format="%d")
        
        try:
            x = mask['TIMESTAMP']
            # Criando o objeto do gráfico
            fig1 = go.Figure()

            # Funções 'add_trace' para criar as linhas do gráfico
            fig1.add_trace(go.Scatter(x=x, y=dft["wnd_spd"],
                                    mode='lines',
                                    name='Taxa de aparecimento do 1º sintoma'))
                                                    
            # Formatando o layout do gráfico
            fig1.update_layout(title='Série temporal completa',
                            xaxis_title='Meses',
                            yaxis_title='Velocidade (m/s)',
                            width=900,
                            height=600)

            # Exibindo o elemento do gráfico na página                
            st.plotly_chart(fig1)

            """ Aqui são apresentados os valores de média Mensal"""	

            st.title("Tabela de Médias Mensais")
            st.write(dto)  


            x2 = dto.index
            # Criando o objeto do gráfico
            fig2 = go.Figure()

            # Funções 'add_trace' para criar as linhas do gráfico
            fig2.add_trace(go.Scatter(x=x2, y=dto["wnd_spd"],
                                    mode='lines',
                                    name='Média Mensal'))

            fig2.add_trace(go.Scatter(x=x2, y=result.seasonal,
                                    mode='lines',
                                    name='Sazonalidade Mensal'))

            fig2.add_trace(go.Scatter(x=x2, y=result.trend,
                                    mode='lines',
                                    name='Tencência Mensal'))                                                    
            # Formatando o layout do gráfico
            fig2.update_layout(title='Média mensal para velocidade do vento',
                            xaxis_title='Meses',
                            yaxis_title='Velocidade (m/s)',
                            width=1000,
                            height=600)

            # Exibindo o elemento do gráfico na página                
            st.plotly_chart(fig2)

            """ Aqui são apresentados os valores de desvio Padrão diário"""

            st.title("Tabela de Desvio Padrão diário")
            st.write(dtd)  

            x3 = dtd.index
            # Criando o objeto do gráfico
            fig3 = go.Figure()

            # Funções 'add_trace' para criar as linhas do gráfico
            fig3.add_trace(go.Scatter(x=x3, y=dtd["wnd_spd"],
                                    mode='lines',
                                    name='Média diária'))
                                                    
            # Formatando o layout do gráfico
            fig3.update_layout(title='Média diária para velocidade do vento',
                            xaxis_title='Dias',
                            yaxis_title='Velocidade (m/s)',
                            width=1000,
                            height=600)

            # Exibindo o elemento do gráfico na página                
            st.plotly_chart(fig3)
            
            if carregar_dados:
                st.subheader('Dados')
                dados = st.dataframe(dto)
        except Exception as e:
            st.error(e)





#Inicio da Parte do código que carrega os dados da base Meteostat e plota os dados a partir das funções horaria, diária e mensal. 

if genre == 'Meteostat': 


    country_select = st.sidebar.selectbox("Selecione o país:", countries)

    stock_select = st.sidebar.selectbox("Selecione a cidade:", cidades)

    from_date = st.sidebar.date_input('De:', start_date)
    to_date = st.sidebar.date_input('Para:', end_date)

    interval_select = st.sidebar.selectbox("Selecione o interval:", intervals)

    carregar_dados = st.sidebar.checkbox('Carregar dados') 


    st.subheader('Visualização gráfica')


    grafico_line = st.empty()

        
    st.title('Análise preliminar de sítio eólico') #elementos centrais da página


    if from_date > to_date:
        st.sidebar.error('Data de ínicio maior do que data final')
    elif interval_select == "Diária":
        df, result = consultar_dados_daily(format_date(from_date), format_date(to_date))
        try:
            
            x = df.index
            fig1 = go.Figure()

            # Funções 'add_trace' para criar as linhas do gráfico
            fig1.add_trace(go.Scatter(x=x, y=df["wspd"],
                                    mode='lines',
                                    name='Série temporal de Velocidade'))
            # Funções 'add_trace' para criar as linhas do gráfico
            fig1.add_trace(go.Scatter(x=x, y=result.seasonal,
                                    mode='lines',
                                    name='Sazonalidade Diária'))    
            # Funções 'add_trace' para criar as linhas do gráfico
            fig1.add_trace(go.Scatter(x=x, y=result.trend,
                                    mode='lines',
                                    name='Tendência Diária'))
            # Formatando o layout do gráfico
            fig1.update_layout(title='Série temporal completa',
                            xaxis_title='Data',
                            yaxis_title='Velocidade (m/s)',
                            width=900,
                            height=600)

            # Exibindo o elemento do gráfico na página                
            st.plotly_chart(fig1)
            
            
            if carregar_dados:
                st.subheader('Dados')
                dados = st.dataframe(df)
        except Exception as e:
            st.error(e)

    elif interval_select == "Mensal":

        df = consultar_dados_hourly(format_date(from_date), format_date(to_date))
        try:
            x = df.index
            fig1 = go.Figure()

            # Funções 'add_trace' para criar as linhas do gráfico
            fig1.add_trace(go.Scatter(x=x, y=df["wspd"],
                                    mode='lines',
                                    name='Série temporal de Velocidade'))
            # Funções 'add_trace' para criar as linhas do gráfico
            fig1.add_trace(go.Scatter(x=x, y=result.seasonal,
                                    mode='lines',
                                    name='Sazonalidade Diária'))    
            # Funções 'add_trace' para criar as linhas do gráfico
            fig1.add_trace(go.Scatter(x=x, y=result.trend,
                                    mode='lines',
                                    name='Tendência Diária'))
            # Formatando o layout do gráfico
            fig1.update_layout(title='Série temporal completa',
                            xaxis_title='Data',
                            yaxis_title='Velocidade (m/s)',
                            width=900,
                            height=600)

            # Exibindo o elemento do gráfico na página                
            st.plotly_chart(fig1)
            
            if carregar_dados:
                st.subheader('Dados')
                dados = st.dataframe(df)
        except Exception as e:
            st.error(e)


#Fim da Parte do código que carrega os dados da base Meteostat e plota os dados a partir das funções horaria, diária e mensal.
