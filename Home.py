import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon= ""
    
)

#image_path='lion.jpg'
            
image = Image.open('lion.jpg')
st.sidebar.image(image, width = 120)

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write('# Curry Company Growth Dashboard')

st.markdown(
    """ Growth Dashboard foi construido para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
    ### Como utilizar o Growth Dashboard?
    - Visão empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geografica: Insights de geolocalização.
    - Visão Entregadores:
        - Acompanha os indicadores semanais de crescimento.
    - Visão Restaurante:
        - Indicadores semanais de crescimento dos restaurantes.
    ### ask for Help
        -Time de Data Science no Discord
            - @gabriel
    """ )
