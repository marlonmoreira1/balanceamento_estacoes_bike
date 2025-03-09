import streamlit as st
from cards import create_card
from rotas.main_map import show_map_static, create_station_map
from streamlit.errors import StreamlitInvalidColumnSpecError

def main_visual(df_filtered,city):

    try:
        status_count = df_filtered["station_type_situation"].value_counts()

        status_colors = {
            'doadora': 'blue',
            'vazia': 'red',
            'risco': 'orange',
            'normal': 'green',
            'indisponivel': 'gray',
            "Outro": "#6c757d" 
        }

        num_cols = max(1, df_filtered['station_type_situation'].nunique())
        status_cols = st.columns(num_cols)

        for status_col, (status, count) in zip(status_cols ,status_count.items()):
            with status_col:
                color = status_colors.get(status, status_colors["Outro"])
                st.markdown(create_card(status, count, color), unsafe_allow_html=True)
        
    
    except StreamlitInvalidColumnSpecError as e:

        pass
        
    st.header(f"Mapa das Estações Completo de {city}")

    mapa_principal = create_station_map(df_filtered)

    show_map_static(mapa_principal,filtro=city)   

