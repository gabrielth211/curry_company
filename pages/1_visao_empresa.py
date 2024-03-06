# Libraries
from haversine import haversine
import folium
import plotly
import plotly.express as px
import plotly.graph_objects as go


# Bibliotecas necessarias
import pandas as pd
import streamlit as st
from PIL import Image
from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Empresa', page_icon='',layout='wide')

#--------------------------------------------------------------------
#-----------------------Funções---------------------------------------
#--------------------------------------------------------------------
def order_by_share(df1):

        df_aux1 = (df1.loc[:, ['ID', 'week_of_year']].groupby( 'week_of_year' ).count().reset_index())
        df_aux2 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby( 'week_of_year').nunique().reset_index()
        df_aux = pd.merge( df_aux1, df_aux2, how='inner', on= 'week_of_year' )
        df_aux['order_by_delivery'] = df_aux['ID'] / df_aux['Delivery_person_ID']
            # gráfico
        fig = px.line( df_aux, x='week_of_year', y='order_by_delivery' )
        return fig

def country_maps(df1):
        columns = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
        columns_groupby = ['City', 'Road_traffic_density']
        data_plot = df1.loc[:, columns].groupby( columns_groupby ).median().reset_index()
        data_plot = data_plot[data_plot['City'] != 'NaN']
        data_plot = data_plot[data_plot['Road_traffic_density'] != 'NaN']
        # Desenhar o mapa
        map_ = folium.Map( zoom_start=11 )
        for index, location_info in data_plot.iterrows():
          folium.Marker( [location_info['Delivery_location_latitude'],
                        location_info['Delivery_location_longitude']],
                        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map_ )
            
        folium_static(map_, width=1024 , height=600)
        

def order_by_week(df1):
        df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
        df_aux =df1.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
        #desenhando grafico de linhas
        fig = px.line(df_aux, x='week_of_year',y='ID')
        return fig

def traffic_city(df1):
        df_aux = df1.loc[:,['ID','City','Road_traffic_density']].groupby(['City','Road_traffic_density']
                                                                                    ).count().reset_index()
        df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN',:]
        df_aux = df_aux.loc[df_aux['City'] != 'NaN',:]
            
        fig = px.scatter(df_aux, x='City',y='Road_traffic_density', size='ID', color = 'City')
        return fig

def traffic_order(df1):
        df_aux = df1.loc[:,['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
        df_aux = df_aux.loc[df_aux['Road_traffic_density'] != 'NaN',:]
        df_aux['entregas_percent'] = df_aux['ID'] / df_aux['ID'].sum()
        #plotar grafico de pizza
        fig = px.pie(df_aux, values = 'entregas_percent', names='Road_traffic_density')
        return fig



def order_byday(df1):
        cols = ["ID", 'Order_Date']
        
        # Seleção de linhas
        df_aux = df1.loc[:, cols].groupby('Order_Date').count().reset_index()
        #desenhar Grafico
        # Plotly
        fig = px.bar(df_aux, x='Order_Date', y='ID')
    
        return fig

def clean_code(df1) :
    """ Essa funão tem a responsabilidade de limpar o DataFrame
    Tipos de limpeza:
    1.Remoão dos dados NaN
    2. Mudança do tipo de variaveis das colunas
    3.Remoção dos espços em texto
    4. formatação de datas
    5. Limpeza da coluna tempo : ( remoção de texto das variaveis numéricas)

    Input: DataFrame
    Output: Dataframe    
    
    """

    # 1. limpeza dos dados
    sem_vazios = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[sem_vazios , :].copy()
    
    sem_vazios = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[sem_vazios , :].copy()
    
    sem_vazios = (df1['City'] != 'NaN ')
    df1 = df1.loc[sem_vazios , :].copy()
    
    sem_vazios = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[sem_vazios , :].copy()
    
    df1 = df1.dropna(subset=['Time_taken(min)'])
    df1 = df1.dropna(subset=['Order_Date'])
    
    
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    #mudar delivery person ratins para float
    
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    # mudando order date de object para data
    df1['datetime'] = df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    
    #convertendo multiples delivery
    
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias , :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    
    #import re
    #numero_de_repeticoes = len(df1)
    #for i in range(numero_de_repeticoes):
     # df1.loc[i, 'Time_taken(min)'] = re.findall( r'\d+', df1.loc[i, 'Time_taken(min)'] )
    
    #df1 = df1.reset_index(drop=True)
    #quantidade_de_linhas = len(df1)
    
    #for i in range(quantidade_de_linhas):
     # df1.loc[i , 'Type_of_order'] = df1.loc[i , 'Type_of_order'].strip()
    
    #RETIRANDO ESPAÇOS DENTRO DE STRINGS
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()
    df1.loc[:,'Time_taken(min)'] = df1.loc[:,'Time_taken(min)'].str.strip()
    
    #removendo str 'min' em Time taken(min)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(str)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min)') [1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    return df1
#---------------------------- Inicio Da EstruturaLógica de Código -------------------------------
    # Importando Dataset
df = pd.read_csv('./datasets/train.csv')
#df1 = df.copy()
df1 = clean_code(df)


# visão:empresa

#==========================================================================================
# Fazendo Barra Lateral
#===============================================================
st.header('Marketplace - Visão Cliente')

image_path = 'lion.jpg'
image = Image.open(image_path)
st.sidebar.image(image, width=120)
                
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')
from datetime import datetime
#Filtro de Datas ======/=======
date_slider = st.sidebar.slider(
   'Até qual data',
   value = datetime(2022, 4, 13),
   min_value = datetime(2022, 2, 11),
   max_value = datetime(2022, 4, 6),
   format = 'DD-MM-YYYY')
linhas_selecionadas = df1["Order_Date"] < date_slider
df1=df1.loc[linhas_selecionadas,:]
st.sidebar.markdown("""___""")

#======Filtro de Trânsito=========

traffic_options =st.sidebar.multiselect(
    'Quais as condições de transito',
    ['Low','Medium', 'High', 'Jam'],
    default = ['Low','Medium', 'High', 'Jam'])
linhas_selecionadas = df1["Road_traffic_density"].isin(traffic_options)
df1=df1.loc[linhas_selecionadas,:]
st.sidebar.markdown("""___""")
st.sidebar.markdown("### Powered by Gabriel")



#=========================================
## ======= Layout no streamlit
#==========================================

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática','Visão Geografica'])

with tab1:
    with st.container():
        st.markdown('# Order by Day')
        fig = order_byday(df1)
        
        st.plotly_chart(fig, use_container_width = True)

    with st.container():        
        col1, col2 =  st.columns(2)
        with col1:
            st.header('Traffic Order Share')
            fig = traffic_order(df1)
            
            st.plotly_chart(fig, use_container_width = True)
            
        
        with col2:
            st.header(' Traffic Order City')
            fig = traffic_city(df1)
            
            
            st.plotly_chart(fig, use_container_width = True)    

with tab2:
    with st.container():
        st.markdown('# Order by Week')
        fig =order_by_week(df1)
        
        st.plotly_chart(fig, use_container_width = True)

    with st.container():
        st.markdown('## Order Share by Week')
        fig = order_by_share(df1)
        
        st.plotly_chart(fig, use_container_width = True)

    
        
with tab3:
    st.header('Country Maps')
    country_maps(df1)

    



