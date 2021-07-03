from numpy import datetime64
import streamlit as st
import pandas as pd
import investpy as ip
from datetime import datetime, timedelta
import plotly.graph_objs as go
import matplotlib.pyplot as plt
from bokeh.plotting import figure
from meteostat import Stations, Daily, Hourly, Monthly
import numpy as np


countries = ['brazil','united states']
intervals = ['Hourly', 'Daily', 'Monthly']
cidades = ["Goiânia", "Fortaleza", "Natal", "Brasília"]

start_date = datetime.now()-timedelta(days=30)
end_date = datetime.now()

ende = datetime.now() - timedelta(days=365)
stop = datetime.now()


@st.cache
def consultar_dados_hourly(from_date, to_date):

    dataH = Hourly(83423, start = ende, end = stop)
    
    dfH = dataH.fetch()   

    return dfH



@st.cache
def consultar_dados_daily(from_date, to_date):

    stations = Stations()

    stations = stations.nearby(-16.2333,  -48.9667 )

    station = stations.fetch()

    data = Daily(83423, start = from_date, end = to_date)
    df = data.fetch()
    
    return(df)
# Função para formatar datas
def format_date(dt, format='%Y-%m-%d %H:%M:%S'):
    
    return dt.strftime(format)


def format_date_dia(dt, format='%y-%m-%d'):
    
    return dt.strftime(format)


@st.cache
def excel_dados_daily(data_excelI, data_excelF):
    
    mask = dft.loc[(pd.to_datetime(dft["TIMESTAMP"]) >= data_excelI) & (pd.to_datetime(dft["TIMESTAMP"]) <= data_excelF)] 
    #mask.set_index('TIMESTAMP', inplace=True)

    

    dto = (mask.groupby(pd.to_datetime(mask["TIMESTAMP"]).dt.strftime('%j')).mean())

    
    return mask, dto

    
def media_diaria():

    df = pd.DataFrame(index=pd.date_range('2015-01-01', '2015-12-31'))

    print(df.groupby(df.index.strftime("%j")).mean())







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

    dft = dft.replace(np.nan,0)


    #dft.to_excel('C:/Users/bacab/OneDrive/Área de Trabalho/Projeto_BRAMS/Dados_Cerrado/dados_temporario.xlsx', index = False)

    dft = pd.read_excel('C:/Users/bacab/OneDrive/Área de Trabalho/Projeto_BRAMS/Dados_Cerrado/dados_temporario.xlsx')



    date = list(dft["TIMESTAMP"])

    dateI = pd.to_datetime(date[0], format='%d-%m-%Y')
    dateF = pd.to_datetime(date[-1], format='%d-%m-%Y')

    data_excelI = st.sidebar.date_input('Data inicial:', dateI)
    data_excelF = st.sidebar.date_input('Data final:', dateF)

    interval_select = st.sidebar.selectbox("Análise:", intervals)
    
    carregar_dados = st.sidebar.checkbox('Carregar dados') 

    st.title('Análise preliminar de sítio eólico') #elementos centrais da página

    st.write(dft)


    if data_excelI > data_excelF:
        st.sidebar.error('Data de ínicio maior do que data final')
    elif interval_select == "Daily":

        mask, dto = excel_dados_daily(format_date(data_excelI), format_date(data_excelF))

        tempo = pd.to_datetime(mask["TIMESTAMP"], format="%d")

        try:

            fig = plt.figure()
            ax = fig.add_subplot(1,1,1)

            ax.plot(
                tempo,
                mask["wnd_spd"],
            )

            ax.set_xlabel("Tempo (dias)")
            ax.set_ylabel("velocidade (m/s)")
            ax.grid(True)
            ax.set_xlim(min(mask["TIMESTAMP"]), max(mask["TIMESTAMP"]))

            st.write(fig)


            
            st.title("Tabela de Médias diária")
            st.write(dto)  

            grafico_line = st.line_chart(dto["wnd_spd"])
            
            if carregar_dados:
                st.subheader('Dados')
                dados = st.dataframe(mask)
        except Exception as e:
            st.error(e)

    elif interval_select == "Hourly":

        dfH = consultar_dados_hourly(format_date(data_excelI), format_date(data_excelF))
        try:
            grafico_line = st.line_chart(dfH["wspd"])
            
            if carregar_dados:
                st.subheader('Dados')
                dados = st.dataframe(dfH)
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
    elif interval_select == "Daily":
        df = consultar_dados_daily(format_date(from_date), format_date(to_date))
        try:
            grafico_line = st.line_chart(df["wspd"])
            
            if carregar_dados:
                st.subheader('Dados')
                dados = st.dataframe(df)
        except Exception as e:
            st.error(e)

    elif interval_select == "Hourly":

        dfH = consultar_dados_hourly(format_date(from_date), format_date(to_date))
        try:
            grafico_line = st.line_chart(dfH["wspd"])
            
            if carregar_dados:
                st.subheader('Dados')
                dados = st.dataframe(dfH)
        except Exception as e:
            st.error(e)


#Fim da Parte do código que carrega os dados da base Meteostat e plota os dados a partir das funções horaria, diária e mensal.
