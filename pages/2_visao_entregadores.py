# Libraries
import haversine
from haversine import haversine
import plotly
import plotly.express as px
import plotly.graph_objects as go


# bibliotecas necessárias
import folium
import pandas as pd
import streamlit as st
from PIL import Image
from datetime import datetime

from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Entregadores', page_icon='',layout='wide')

#-----------------------------------------------
#---------------- Funções-----------------------

def top_deliver(df1, faster):
            
        df2 = ( df1.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                   .groupby( ['City', 'Delivery_person_ID'] )
                   .mean()
                   .sort_values( ['City', 'Time_taken(min)'], ascending= faster ).reset_index() )
    
        df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
        df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
        df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    
        df3 = pd.concat( [df_aux01, df_aux02, df_aux03] ).reset_index( drop=True )
                
        return df3

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


# Import dataset 
df = pd.read_csv( './datasets/train.csv' )

df1 = df.copy()
# cleaning dataframe
df1 = clean_code(df)


# =======================================
# Barra Lateral
# =======================================
st.header( 'Marketplace - Visão Entregadores' )

#image_path = 'lion.jpg'
image = Image.open( 'lion.jpg' )
st.sidebar.image( image, width=120 )

st.sidebar.markdown( '# Cury Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """---""" )

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



# =======================================
# Layout no Streamlit
# =======================================
tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '_', '_'] )
st.markdown("""---""")

with tab1:
    with st.container():
        st.title( 'Overall Metrics' )
        
        col1, col2, col3, col4 = st.columns( 4, gap='large' )
        with col1:
            # A maior idade dos entregadores
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric( 'Maior idade', maior_idade )

            
        with col2:
            # A menor idade dos entregadores
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric( 'Menor idade', menor_idade )
            
        with col3:
            # A maior idade dos entregadores
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric( 'Melhor condicao', melhor_condicao )
            
        with col4:
            # A menor idade dos entregadores
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric( 'Pior condicao', pior_condicao )
            
    with st.container():
        st.markdown( """---""" )
        st.title( 'Avaliacoes' )
        
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '##### Avalicao medias por Entregador' )
            df_avg_ratings_per_deliver = ( df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                                              .groupby( 'Delivery_person_ID' )
                                              .mean()
                                              .reset_index() )
            st.dataframe( df_avg_ratings_per_deliver )
                
        with col2:
            st.markdown( '##### Avaliacao media por transito' )
            df_avg_std_rating_by_traffic = ( df1.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                                .groupby( 'Road_traffic_density')
                                                .agg( {'Delivery_person_Ratings': ['mean', 'std' ]} ) )

            # mudanca de nome das colunas
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']

            # reset do index
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            st.dataframe( df_avg_std_rating_by_traffic )
            
            
            
            st.markdown( '##### Avaliacao media por clima' )
            df_avg_std_rating_by_weather = ( df1.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                                .groupby( 'Weatherconditions')
                                                .agg( {'Delivery_person_Ratings': ['mean', 'std']} ) )

            # mudanca de nome das colunas
            df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std']

            # reset do index
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
            st.dataframe( df_avg_std_rating_by_weather )
            
    
    with st.container():
        st.markdown( """---""" )
        st.title( 'Velocidade de Entrega' )
        
        col1, col2 = st.columns( 2 )
        
        with col1:
            st.markdown( '##### Top Entregadores mais rapidos' )
            df3 = top_deliver(df1, faster = True)
                              
            st.dataframe( df3 )
            
        with col2:
            st.markdown( '##### Top Entregadores mais lentos' )
            df3 = top_deliver(df1, faster = False)
                              
            st.dataframe( df3 )
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
            
                         
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
