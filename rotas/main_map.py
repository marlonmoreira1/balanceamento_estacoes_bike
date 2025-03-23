import folium
from folium import FeatureGroup, plugins
from typing import Tuple, Dict
import pandas as pd
import streamlit as st
import tempfile
import base64


def create_station_map(df_stations: pd.DataFrame) -> folium.Map:
    """
    Cria um mapa Folium com todas as estações, categorizadas por tipo de situação e
    conecta as estações vazias às suas respectivas estações doadoras com linhas retas.
    
    Parameters:
    - df_stations (pd.DataFrame): DataFrame com informações das estações. Deve conter:
        - 'station_id': ID da estação
        - 'name': Nome da estação
        - 'address': Endereço da estação
        - 'lat': Latitude da estação
        - 'lon': Longitude da estação
        - 'station_type_situation': Situação da estação (doadora, vazia, risco, normal)
    - df_pairs (pd.DataFrame): DataFrame com pares de estações vazia e doadora. Deve conter:
        - 'station_id': ID da estação vazia
        - 'name': Nome da estação vazia
        - 'lat': Latitude da estação vazia
        - 'lon': Longitude da estação vazia
        - 'nearby_station_id': ID da estação doadora
        - 'name_nearby': Nome da estação doadora
        - 'lat_nearby': Latitude da estação doadora
        - 'lon_nearby': Longitude da estação doadora

    Returns:
    - folium.Map: Mapa com todas as estações e conexões entre estações vazias e doadoras.
    """
   
    center_lat = df_stations['lat'].median()
    center_lon = df_stations['lon'].median()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    
    station_colors = {
        'doadora': 'blue',
        'vazia': 'red',
        'risco': 'orange',
        'normal': 'green',
        'indisponivel': 'gray'
    }

    
    for _, row in df_stations.iterrows():

        popup_text = f"""
            <div style="font-family: Arial; padding: 5px;">
                <h4 style="margin: 0;">🚲 {row['name']}</h4>                
                <p style="margin: 5px 0;">Disponível/Capacidade: {row['num_bikes_available']}/{row['capacity']}</p>                                             
            </div>
        """

        if pd.notnull(row['lat']) and pd.notnull(row['lon']):
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=popup_text,
                icon=folium.Icon(color=station_colors.get(row['station_type_situation'], 'gray'))
            ).add_to(m)
            
    return m

def get_map_html(mapa):
    
    m = mapa
    html_string = m.get_root().render()
    
    
    html_string = html_string.replace(
        '</head>',
        '''
        <style>
        #map {
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;
            z-index: 0;
        }
        .folium-map {
            width: 100%;
            height: 600px;
            position: relative;
        }
        </style>
        </head>
        '''
    )
    
    return html_string

#@st.cache_data(show_spinner=False)
def get_cached_map_html(mapa):
    return mapa

def show_map_static(mapa, filtro):
    
    map_html = get_cached_map_html(get_map_html(mapa) + filtro)
    st.components.v1.html(map_html, height=600)
