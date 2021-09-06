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
import os
from matplotlib.backends.backend_agg import RendererAgg
from  geopy.geocoders import Nominatim
import seaborn as sns
import matplotlib
from matplotlib.figure import Figure
from PIL import Image

matplotlib.use("agg")



class Excel_read():
    # Função para formatar datas
    def format_date(self, dt, format='%Y-%m-%d %H:%M:%S'):
        
        return dt.strftime(format)


    def format_date_dia(self, dt, format='%d-%m'):
        
        return dt.strftime(format)

    @st.cache
    def excel_dados_horaria(self, data_excelI, data_excelF):
        
        self.mask = self.dft.loc[(pd.to_datetime(self.dft["TIMESTAMP"]) >= data_excelI) & (pd.to_datetime(self.dft["TIMESTAMP"]) <= data_excelF)] 
        #mask.set_index('TIMESTAMP', inplace=True)
    
        self.dto = self.mask.groupby(pd.to_datetime(self.mask["TIMESTAMP"]).dt.strftime('%Y %j:%H')).mean()

        self.dtd = self.mask.groupby(pd.to_datetime(self.mask["TIMESTAMP"]).dt.strftime('%Y %j:%H')).std()

        self.periodo = int(len(self.dto)/2)

        self.result = seasonal_decompose(self.dto["wnd_spd"], model='additive', extrapolate_trend='freq', period= self.periodo)

        return self.mask, self.dto, self.dtd, self.result

    @st.cache
    def excel_dados_diaria(self, data_excelI, data_excelF):
        
        self.mask = self.dft.loc[(pd.to_datetime(self.dft["TIMESTAMP"]) >= data_excelI) & (pd.to_datetime(self.dft["TIMESTAMP"]) <= data_excelF)] 
        #mask.set_index('TIMESTAMP', inplace=True)
    
        self.dto = self.mask.groupby(pd.to_datetime(self.mask["TIMESTAMP"]).dt.strftime('%Y-%m %j')).mean()

        self.dtd = self.mask.groupby(pd.to_datetime(self.mask["TIMESTAMP"]).dt.strftime('%Y-%m')).std()

        self.periodo = int(len(self.dto)/2)

        self.result = seasonal_decompose(self.dto["wnd_spd"], model='additive', extrapolate_trend='freq', period= self.periodo)

        return self.mask, self.dto, self.dtd, self.result

    @st.cache
    def excel_dados_mensal(self, data_excelI, data_excelF):
        
        self.mask = self.dft.loc[(pd.to_datetime(self.dft["TIMESTAMP"]) >= data_excelI) & (pd.to_datetime(self.dft["TIMESTAMP"]) <= data_excelF)] 
        
        self.dto = self.mask.groupby(pd.to_datetime(self.mask["TIMESTAMP"]).dt.strftime('%Y-%m')).mean()  
        
        self.dtd = self.mask.groupby(pd.to_datetime(self.mask["TIMESTAMP"]).dt.strftime('%Y-%m')).std()

        self.dt_max = self.mask.groupby(pd.to_datetime(self.mask["TIMESTAMP"]).dt.strftime('%m')).max()

        self.periodo = int(len(self.dto)/2)

        self.result = seasonal_decompose(self.dto["wnd_spd"], model='additive', extrapolate_trend='freq', period= self.periodo)

        print(self.dto["wnd_spd"], self.dt_max["wnd_spd"], self.dtd["wnd_spd"])

        return self.mask, self.dto, self.dtd, self.result

    def file_selector(self):

        uploaded_file = st.sidebar.file_uploader("Escolha o arquivo", type = ['csv', 'xlsx'])

        return uploaded_file

    def excel_leitura(self, uploaded_file):
        
        self.int = ['Horária', 'Diária', 'Mensal']
        
        # uploaded_file = st.sidebar.file_uploader("Escolha o arquivo", type = ['csv', 'xlsx'])

        if uploaded_file is not None:

            try:
                self.dft = pd.read_excel(uploaded_file, index_col=None)
            except:
                self.dft = pd.read_excel(uploaded_file, index_col=None)

        self.dft = self.dft.drop(self.dft.index[0:3])

        self.dft.columns = ["TIMESTAMP", "wnd_spd", "rslt_wnd_spd", "wnd_dir_sonic", "std_wnd_dir", "wnd_dir_compass", "Ux_Avg",	"Uy_Avg",
                        "Uz_Avg", "u_star",	"Ux_stdev",	"Ux_Uy_cov", "Ux_Uz_cov", "Uy_stdev", "Uy_Uz_cov", "Uz_stdev"]
        
        self.dft = pd.DataFrame(self.dft)

        self.dft.ffill(inplace=True)

        date = list(self.dft["TIMESTAMP"])

        self.dateI = pd.to_datetime(date[0], format='%d-%m-%Y')
        self.dateF = pd.to_datetime(date[-1], format='%d-%m-%Y')

        #self.interval_select = st.sidebar.selectbox("Análise:", self.int)  
        self.carregar_dados = st.sidebar.checkbox('Carregar dados') 

        st.title('Análise preliminar de sítio eólico') #elementos centrais da página

        st.write(self.dft)

        return (self.dateI, self.dateF)

        #dft = dft.rename(columns={'TIMESTAMP':'index'}).set_index('index')

    def grafico_excel(self, mask, dto, dtd, result, freq, legenda):


        self.x = self.mask['TIMESTAMP']

        fig1 = go.Figure()

        # Funções 'add_trace' para criar as linhas do gráfico
        fig1.add_trace(go.Scatter(x= self.x, y= self.dft["wnd_spd"],
                                mode='lines',
                                name='Média de velocidade'))
                                                
        # Formatando o layout do gráfico
        fig1.update_layout(title='Série temporal completa',
                        xaxis_title= legenda,
                        yaxis_title='Velocidade (m/s)',
                        width=900,
                        height=600)

        # Exibindo o elemento do gráfico na página                
        st.plotly_chart(fig1)

        """ Aqui são apresentados os valores de média """ + str(freq)	

        st.title("Tabela de Média " + str(freq))
        st.write(self.dto)  


        self.x2 = self.dto.index
        # Criando o objeto do gráfico
        fig2 = go.Figure()

        # Funções 'add_trace' para criar as linhas do gráfico
        fig2.add_trace(go.Scatter(x= self.x2, y= self.dto["wnd_spd"],
                                mode='lines',
                                name='Média ' + str(freq)))

        fig2.add_trace(go.Scatter(x= self.x2, y= self.result.seasonal,
                                mode='lines',
                                name='Sazonalidade ' + str(freq)))

        fig2.add_trace(go.Scatter(x= self.x2, y= self.result.trend,
                                mode='lines',
                                name='Tencência ' + str(freq)))                                                    
        # Formatando o layout do gráfico
        fig2.update_layout(title='Média ' + str(freq) + ' para velocidade do vento',
                        xaxis_title= legenda,
                        yaxis_title='Velocidade (m/s)',
                        width=1000,
                        height=600)

        # Exibindo o elemento do gráfico na página                
        st.plotly_chart(fig2)  

class Meteostat_read():

    def info_dados(self):

        intervals = ['Horária', 'Diária', 'Mensal']
        cidades = ["Goiânia", "Fortaleza", "Natal", "Brasília"]

        start_date = datetime.now()-timedelta(days=365)
        end_date = datetime.now()

        ende = datetime.now() - timedelta(days=365)
        stop = datetime.now()

        return (intervals, cidades, start_date, end_date)

    def estacao_cidade(self, stock_select):
        
        geolocator = Nominatim(user_agent='myapplication')
        city = str(stock_select)
        country = "Brazil"
        loc = geolocator.geocode(city+','+ country)

        self.latitude, self.longitude = loc.latitude, loc.longitude
        
        stations = Stations()

        stations = stations.nearby(self.latitude, self.longitude)

        self.station = stations.fetch()

        return (self.station.index[0])

    @st.cache
    def consultar_dados_hourly(self, from_date, to_date):

        data = Hourly(self.station.index[0], start = from_date, end = to_date)
        
        self.df = data.fetch() 

        self.periodo = int(len(self.df["wspd"])/2)

        print(from_date, to_date)

        self.result = seasonal_decompose(self.df["wspd"], model='additive', extrapolate_trend='freq', period= self.periodo)

        return self.df, self.result

    @st.cache
    def consultar_dados_daily(self, from_date, to_date):

        data = Daily(self.station.index[0], start = from_date, end = to_date)
        self.df = data.fetch()

        self.periodo = int(len(self.df[["wspd"]])/2)

        print(len(self.df[["wspd"]]))

        self.result = seasonal_decompose(self.df["wspd"], model='additive', extrapolate_trend='freq', period= self.periodo)

        return self.df, self.result

    @st.cache
    def consultar_dados_monthly(self, from_date, to_date):

        data = Monthly(self.station.index[0], start = from_date, end = to_date)
        
        self.df = data.fetch() 

        self.periodo = int(len(self.df["wspd"])/2)

        print(from_date, to_date)

        self.result = seasonal_decompose(self.df["wspd"], model='additive', extrapolate_trend='freq', period= self.periodo)

        return self.df, self.result


    def format_date(self, dt, format='%Y-%m-%d %H:%M:%S'):
        
        return dt.strftime(format)


    def format_date_dia(self, dt, format='%d-%m'):
        
        return dt.strftime(format)

    def grafico_meteostat(self, df, result, freq, legenda):


        self.x = self.df.index

        fig1 = go.Figure()

        # Funções 'add_trace' para criar as linhas do gráfico
        fig1.add_trace(go.Scatter(x= self.x, y= self.df["wspd"],
                                mode='lines',
                                name='Média de velocidade'))
                                                
        # Formatando o layout do gráfico
        fig1.update_layout(title='Série temporal completa',
                        xaxis_title= legenda,
                        yaxis_title='Velocidade (m/s)',
                        width=900,
                        height=600)

        # Exibindo o elemento do gráfico na página                
        st.plotly_chart(fig1)


        self.x2 = self.df.index
        # Criando o objeto do gráfico
        fig2 = go.Figure()

        # Funções 'add_trace' para criar as linhas do gráfico
        fig2.add_trace(go.Scatter(x= self.x2, y= self.df["wspd"],
                                mode='lines',
                                name='Média ' + str(freq)))

        fig2.add_trace(go.Scatter(x= self.x2, y= self.result.seasonal,
                                mode='lines',
                                name='Sazonalidade ' + str(freq)))

        fig2.add_trace(go.Scatter(x= self.x2, y= self.result.trend,
                                mode='lines',
                                name='Tencência ' + str(freq)))                                                    
        # Formatando o layout do gráfico
        fig2.update_layout(title='Média ' + str(freq) + ' para velocidade do vento',
                        xaxis_title= legenda,
                        yaxis_title='Velocidade (m/s)',
                        width=1000,
                        height=600)

        # Exibindo o elemento do gráfico na página                
        st.plotly_chart(fig2)  


class layout_tela(Excel_read, Meteostat_read):
    def __init__(self):

        self.intervals = ['Horária', 'Diária', 'Mensal']

        self.genre = st.sidebar.radio("Selecione a fonte de dados",('Excel', 'Meteostat'), index=1)

        uploaded_file =self.file_selector()

        if self.genre == 'Excel':

            try:

                self.dateI, self.dateF = self.excel_leitura(uploaded_file)
                self.int_select = st.sidebar.selectbox("Análise:", self.intervals)

                self.data_excelI = st.sidebar.date_input('Data inicial:', self.dateI)
                self.data_excelF = st.sidebar.date_input('Data final:', self.dateF)

                if self.data_excelI > self.data_excelF:
                    st.sidebar.error('Data de ínicio maior do que data final')

                if self.int_select == "Mensal":

                    self.mask, self.dto, self.dtd, self.result = self.excel_dados_mensal(self.format_date(self.data_excelI), self.format_date(self.data_excelF))  
                    
                    self.grafico_excel(self.mask, self.dto, self.dtd, self.result, "Mensal", "Mês") 

                elif self.int_select == "Horária":     

                    self.mask, self.dto, self.dtd, self.result = self.excel_dados_horaria(self.format_date(self.data_excelI), self.format_date(self.data_excelF))  
                    
                    self.grafico_excel(self.mask, self.dto, self.dtd, self.result, "Horária", "Hora")  

                elif self.int_select == "Diária":     

                    self.mask, self.dto, self.dtd, self.result = self.excel_dados_diaria(self.format_date(self.data_excelI), self.format_date(self.data_excelF))  
                    
                    self.grafico_excel(self.mask, self.dto, self.dtd, self.result, "Diária", "dia")  
            except:
                st.write("Carregue o arquivo Excel")
        if self.genre == 'Meteostat':

            intervals, cidades, start_date, end_date = self.info_dados()

            self.stock_select = st.sidebar.selectbox("Selecione a cidade:", cidades)

            self.int_select = st.sidebar.selectbox("Análise:", intervals)
            self.data_excelI = st.sidebar.date_input('Data inicial:', start_date)
            self.data_excelF = st.sidebar.date_input('Data final:', end_date) 

            self.estacao_cidade(self.stock_select)

            if self.data_excelI > self.data_excelF:

                st.sidebar.error('Data de ínicio maior do que data final')   

            elif self.int_select == "Diária":

                self.df, self.result = self.consultar_dados_daily(self.format_date(self.data_excelI), self.format_date(self.data_excelF)) 

                st.write(self.df)

                self.grafico_meteostat(self.df, self.result, "Diária", "dia")

            elif self.int_select == "Horária":

                self.df, self.result = self.consultar_dados_hourly(pd.to_datetime(self.data_excelI), pd.to_datetime(self.data_excelF)) 

                st.write(self.df)

                self.grafico_meteostat(self.df, self.result, "Horária", "Horas")

            elif self.int_select == "Mensal":

                self.df, self.result = self.consultar_dados_monthly(pd.to_datetime(self.data_excelI), pd.to_datetime(self.data_excelF)) 

                st.write(self.df)

                self.grafico_meteostat(self.df, self.result, "Mensal", "Mês")

                 


layout_tela()
