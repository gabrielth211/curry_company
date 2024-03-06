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


# Import dataset
df = pd.read_csv( 'train.csv' )

df1 = df.copy()

# 1. convertando a coluna Age de texto para numero
linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ') 
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ') 
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['City'] != 'NaN ') 
df1 = df1.loc[linhas_selecionadas, :].copy()

linhas_selecionadas = (df1['Festival'] != 'NaN ') 
df1 = df1.loc[linhas_selecionadas, :].copy()

df1 = df1.dropna(subset=['Time_taken(min)'])

df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

# 2. convertando a coluna Ratings de texto para numero decimal ( float )
df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

# 3. convertando a coluna order_date de texto para data
df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )


# 4. convertendo multiple_deliveries de texto para numero inteiro ( int )
linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
df1 = df1.loc[linhas_selecionadas, :].copy()
df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

## 5. Removendo os espacos dentro de strings/texto/object
#df1 = df1.reset_index( drop=True )
#for i in range( len( df1 ) ):
#  df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()


# 6. Removendo os espacos dentro de strings/texto/object
df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
df1.loc[:,'Time_taken(min)'] = df1.loc[:,'Time_taken(min)'].str.strip()

# 7. Limpando a coluna de time taken
df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(str)
df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split( '(min) ')[1] )
df1['Time_taken(min)']  = df1['Time_taken(min)'].astype( int )


# ==============================================================================
# ------------------------Barra Lateral------------------------------
# ==============================================================================
st.header( 'Marketplace - Visão Restaurantes' )

image_path = 'lion.jpg'
image = Image.open( image_path )
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
            cols =['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
            df1['Distance_delivery'] = df1.loc[:, cols].apply(lambda x: haversine(
                (x['Restaurant_latitude'], x['Restaurant_longitude']),(x['Delivery_location_latitude'],
                                                                       x['Delivery_location_longitude'])),axis=1)
            
            avg_distance = np.round( df1['Distance_delivery'].mean(), 2)
            col2.metric('A distancia Média',avg_distance)
        with col3:
            df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)': ['mean', 'std']}))
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            linhas_selecionadas = df_aux['Festival'] == 'Yes'
            df_aux = np.round(df_aux.loc[linhas_selecionadas, 'avg_time'], 2)
            col3.metric('Tempo médio de entrega c/ Festival', df_aux)
            
        with col4:
            df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)': ['mean', 'std']}))
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            linhas_selecionadas = df_aux['Festival'] == 'Yes'
            df_aux = np.round(df_aux.loc[linhas_selecionadas, 'std_time'], 2)
            col4.metric('Tempo médio de entrega c/ Festival', df_aux)
        with col5:
            df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)': ['mean', 'std']}))
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            linhas_selecionadas = df_aux['Festival'] == 'No'
            df_aux = np.round(df_aux.loc[linhas_selecionadas, 'avg_time'], 2)
            col5.metric('Tempo médio de entrega c/ Festival', df_aux)
            
        with col6:
            df_aux = (df1.loc[:, ['Time_taken(min)', 'Festival']]
                         .groupby('Festival')
                         .agg({'Time_taken(min)': ['mean', 'std']}))
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            linhas_selecionadas = df_aux['Festival'] == 'No'
            df_aux = np.round(df_aux.loc[linhas_selecionadas, 'std_time'], 2)
            col6.metric('Tempo médio de entrega c/ Festival', df_aux)
             
    with st.container(): ### container center
        st.markdown("""---""")
        col1, col2 = st.columns(2)
        with col1:
            df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean', 'std']})
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig= go.Figure()
            fig.add_trace(go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'],
                                 error_y=dict(type='data',array=df_aux['std_time'])))
            fig.update_layout(barmode='group')
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("""---""")
       
            df_aux = (df1.loc[:, ['City', 'Time_taken(min)', 'Type_of_order']]
                     .groupby(['City', 'Type_of_order'])
                     .agg({'Time_taken(min)': ['mean', 'std']}))
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            st.dataframe(df_aux, use_container_width=True)
        
        
        
    with st.container():
        st.markdown("""---""")
        st.markdown('# Distribuição de tempo')

        col1, col2 = st.columns(2, gap='large')
        with col1:
            st.markdown("""---""")
            cols = ['Restaurant_latitude','Restaurant_longitude','Delivery_location_latitude','Delivery_location_longitude']
            df1['Distance_delivery'] = (df1.loc[:, cols]
                                      .apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                                                                 (x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis=1))

            avg_distance = df1.loc[:, ['City', 'Distance_delivery']].groupby('City').mean().reset_index()
            fig = go.Figure( data=[go.Pie(labels = avg_distance['City'], 
                                      values=avg_distance['Distance_delivery'], pull = [0, 0.1, 0])])
            st.plotly_chart(fig, use_container_width=True, use_container_height=True)
            

        
        with col2:
            cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
            df_aux = (df1.loc[:, cols]
                        .groupby(['City','Road_traffic_density'])
                        .agg({'Time_taken(min)': ['mean', 'std']}))
            
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            fig = px.sunburst(df_aux, path = ['City','Road_traffic_density'], values='avg_time', color = 'std_time', 
                              color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std_time']))
            st.plotly_chart(fig, use_container_width=True, use_container_height=True)
        
            
   

















