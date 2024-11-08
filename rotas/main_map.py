import folium
from folium import FeatureGroup, plugins
from typing import Tuple, Dict
import pandas as pd
import streamlit as st
import tempfile
import base64


def create_station_map(df_stations: pd.DataFrame, df_pairs: pd.DataFrame) -> folium.Map:
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
   
    center_lat = df_stations['lat'].mean()
    center_lon = df_stations['lon'].mean()
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    
    station_colors = {
        'doadora': 'blue',
        'vazia': 'red',
        'risco': 'orange',
        'normal': 'green'
    }

    
    for _, row in df_stations.iterrows():
        if pd.notnull(row['lat']) and pd.notnull(row['lon']):
            folium.Marker(
                location=[row['lat'], row['lon']],
                popup=row['name'],
                icon=folium.Icon(color=station_colors.get(row['station_type_situation'], 'gray'))
            ).add_to(m)

    
    for _, row in df_pairs.iterrows():
        if pd.notnull(row['lat']) and pd.notnull(row['lon']) and pd.notnull(row['lat_nearby']) and pd.notnull(row['lon_nearby']):
            folium.PolyLine(
                locations=[[row['lat'], row['lon']], [row['lat_nearby'], row['lon_nearby']]],
                color="blue",
                weight=2,
                opacity=0.7
            ).add_to(m)

    return m



def get_map_html(df_stations, df_pairs):
    """
    Cria o mapa e retorna o HTML como string
    """
    
    m = create_station_map(df_stations, df_pairs)
    
    
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

def show_map_static(df_stations, df_pairs):
    """
    Exibe o mapa usando st.components.html
    """
  
    @st.cache_data
    def get_cached_map_html():
        return get_map_html(df_stations, df_pairs)
    
  
    map_html = get_cached_map_html()
    

    st.components.v1.html(map_html, height=600)