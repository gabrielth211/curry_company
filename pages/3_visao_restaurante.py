# Libraries
from haversine import haversine
import plotly
import plotly.express as px
import plotly.graph_objects as go


# bibliotecas necessárias
import folium
import numpy as np
import pandas as pd
import streamlit as st
from PIL import Image
from datetime import datetime

from streamlit_folium import folium_static

st.set_page_config(page_title='Visão Restaurante', page_icon='',layout='wide')

#----------------------------------------------------------
#-------------------Função---------------------------------
def avg_std_time_on_traffic( df1 ):
        cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
        df_aux = (df1.loc[:, cols]
                    .groupby(['City','Road_traffic_density'])
                    .agg({'Time_taken(min)': ['mean', 'std']}))
                
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()
    
        fig = px.sunburst(df_aux, path = ['City','Road_traffic_density'], values='avg_time', color = 'std_time', 
                                  color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std_time']))
        return fig
     
def avg_std_time_graph( df1):
                
            df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig= go.Figure()
            fig.add_trace(go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'],
                                 error_y=dict(type='data',array=df_aux['std_time'])))
            fig.update_layout(barmode='group')
            return fig

def avg_std_time_delivery( df1, op, festival):
        """ Essa função calcula o tempo médio e desvio padrão do tempo de entrega.
            Parâmetros:
            Input:
                - df: DataFrame com os dados 
                - op: Tipo de Operação a ser calculado
                    'avg_time' : Calcula o tempo médio 
                    'std_time': Calcula o desvio padrão do tempo de entrega
                - festival: ocorrencia de festival
                    'Yes': com festival
                    'No': Sem festival
                output:
                - df: DataFrame com 2 colunas e 1 linha
        """
                    
        df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)': ['mean', 'std']}))
            
        df_aux.columns = ['avg_time', 'std_time']
        df_aux = df_aux.reset_index()

        df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2)
        return df_aux


def delivery_distance(df1, fig):
    if fig == False:
    
        cols =(['Restaurant_latitude','Restaurant_longitude',
                'Delivery_location_latitude','Delivery_location_longitude'])
    
        df1['Distance_delivery'] = (df1.loc[:, cols]
                                       .apply(lambda x:
                                           haversine((x['Restaurant_latitude'],
                                           x['Restaurant_longitude']),
                                           (x['Delivery_location_latitude'],                                                                                  x['Delivery_location_longitude'])),axis=1))
                
        avg_distance = np.round( df1['Distance_delivery'].mean(), 2)
        return avg_distance
    else:
    
        cols =(['Restaurant_latitude','Restaurant_longitude',
                'Delivery_location_latitude','Delivery_location_longitude'])
    
        df1['Distance_delivery'] = (df1.loc[:, cols]
                                       .apply(lambda x:
                                           haversine((x['Restaurant_latitude'],
                                           x['Restaurant_longitude']),
                                           (x['Delivery_location_latitude'],                                                                                  x['Delivery_location_longitude'])),axis=1))        

        avg_distance = df1.loc[:, ['City', 'Distance_delivery']].groupby('City').mean().reset_index()
        fig = go.Figure( data=[go.Pie(labels = avg_distance['City'], values=avg_distance['Distance_delivery'], pull = [0, 0.1, 0])])
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

# Import dataset
df = pd.read_csv( './datasets/train.csv' )
df1 = clean_code(df)
# ==============================================================================
# ------------------------Barra Lateral------------------------------
# ==============================================================================
st.header( 'Marketplace - Visão Restaurantes' )

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



# ======================================================================================
# -------------------------------------Layout no Streamlit------------------------------
# ======================================================================================
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','_','_'])
with tab1:
    with st.container():
        st.subheader('Overal metrics')

        col1, col2, col3, col4, col5, col6, = st.columns(6)
        with col1:
            delivery_unique = len(df1.loc[:, "Delivery_person_ID"].unique())
            col1.metric('Entregadores únicos', delivery_unique) 
            
        with col2:
            avg_distance = delivery_distance(df1, fig = False)
            col2.metric('A distancia média', avg_distance)
            
        with col3:
            df_aux = avg_std_time_delivery(df1, op = 'avg_time', festival = 'Yes')
            
            col3.metric('Tempo médio de entrega c/ Festival', df_aux)
            
        with col4:
            df_aux = avg_std_time_delivery(df1, op = 'avg_time', festival = 'No')
        
            col4.metric('Tempo médio de entrega s/ Festival', df_aux)
            
        with col5:
            df_aux = avg_std_time_delivery(df1, op = 'std_time', festival = 'Yes')
            
            col5.metric('std do Tempo médio de entrega c/ Festival', df_aux)
            
        with col6:
            df_aux = avg_std_time_delivery(df1, op = 'std_time', festival = 'No')
            
            col6.metric('std do Tempo médio de entrega s/ Festival', df_aux)
             
    with st.container(): ### container center
        st.markdown("""---""")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader('Desvio padrão tempo de entregas')
            fig = avg_std_time_graph(df1)
            
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader('Média e Desvio Padrão: Tempo de entrega, por tipo de pedido, por cidade')
            st.markdown("""---""")
       
            df_aux = (df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                     .groupby(['City', 'Type_of_order'])
                     .agg({'Time_taken(min)': ['mean', 'std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            st.dataframe(df_aux, use_container_width=True,)
        
        
        
    with st.container():
        st.markdown("""---""")
        st.markdown('# Distribuição de tempo')

        col1, col2 = st.columns(2, gap='large')
        with col1:
            fig = avg_distance = delivery_distance(df1, fig = True)
            st.plotly_chart(fig, use_container_width=True, use_container_height=True)
            

        
        with col2:
            fig = avg_std_time_on_traffic( df1 )
            
            st.plotly_chart(fig, use_container_width=True, use_container_height=True)
        
