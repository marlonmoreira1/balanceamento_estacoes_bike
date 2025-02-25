import streamlit as st
from cards import create_card
from rotas.main_map import show_map_static, create_station_map


def main_visual(df_filtered,city):

    status_count = df_filtered["station_type_situation"].value_counts()

    status_colors = {
        'doadora': 'blue',
        'vazia': 'red',
        'risco': 'orange',
        'normal': 'green',
        'indisponivel': 'gray',
        "Outro": "#6c757d" 
    }

    status_cols = st.columns(len(df_filtered['station_type_situation'].unique()))

    for status_col, (status, count) in zip(status_cols ,status_count.items()):
        with status_col:
            color = status_colors.get(status, status_colors["Outro"])
            st.markdown(create_card(status, count, color), unsafe_allow_html=True)

    st.header(f"Mapa das Estações Completo de {city}")

    mapa_principal = create_station_map(df_filtered)

    show_map_static(mapa_principal,filtro=city)
    
    

