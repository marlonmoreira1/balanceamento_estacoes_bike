import pandas as pd
import polars as pl
import requests
import folium
from typing import Dict, List, Tuple
import time
import streamlit as st
import random
from folium import plugins, FeatureGroup
import colorsys
from scipy.spatial import distance_matrix
import networkx as nx
from geopy.distance import geodesic
from pares.icons_markers import create_marker_text_and_icon
from rotas.cores_rotas import get_route, generate_distinct_colors
from rotas.main_map import get_map_html
from calculate_routes.distance_matrix import get_distance_matrix


@st.cache_data(ttl=600,show_spinner=False)
def optimize_complete_route_with_map(df_stations,df):
    """
    Otimiza a rota para cobrir todas as estações (doadoras e vazias) em uma única rota,
    obtém as rotas detalhadas entre as estações na sequência otimizada e plota no mapa.

    Parameters:
    df_stations (pd.DataFrame): DataFrame contendo informações das estações e suas distâncias.

    Returns:
    dict: Dicionário com informações da rota otimizada.
    folium.Map: Mapa Folium com a rota otimizada visualizada.
    """

    df_polars = pl.from_pandas(df_stations)    
    complete_df = pl.from_pandas(df)
    stations_df = pl.concat([
        df_polars.select(
            pl.col('name_nearby').alias('station'),
            pl.col('lat_nearby').alias('lat'),
            pl.col('lon_nearby').alias('lon')
        ).with_columns(pl.lit('doadora').alias('type')),
        df_polars.select(
            pl.col('name').alias('station'),
            pl.col('lat').alias('lat'), 
            pl.col('lon').alias('lon')
        ).with_columns(pl.lit('vazia').alias('type'))
    ]).unique(subset='station')    
    
    stations_df = stations_df.sort(by="type", descending=False)
    
    stations_list = stations_df.to_numpy()
    
    G = nx.Graph()
    for i, (station1, lat1, lon1, type1) in enumerate(stations_list):
        for j, (station2, lat2, lon2, type2) in enumerate(stations_list):
            if i != j:
                distance = geodesic((lat1, lon1), (lat2, lon2)).km
                
                
                if type1 == 'vazia' and type2 == 'vazia':
                    distance *= 6
                
                G.add_edge(station1, station2, distance=distance)        
    
    optimized_path = nx.algorithms.approximation.traveling_salesman.christofides(G, weight="distance")    

    start_coords = stations_df.filter(pl.col('station') == optimized_path[0])
    lat = start_coords.select(pl.col('lat')).item()
    lon = start_coords.select(pl.col('lon')).item()
    m = folium.Map(location=[lat, lon], zoom_start=12)

    color = "blue"
    
    total_distance = 0
    total_duration = 0
    detailed_route = []
    
    optimized_coords = [
    stations_df.filter(pl.col('station') == station).select(['lat', 'lon']).row(0)
    for station in optimized_path
    ]
    
    distance_matrix_result = get_distance_matrix(optimized_coords)
    
    for i in range(len(optimized_path)-1):
        start = optimized_path[i]
        end = optimized_path[i+1]
        
        start_coords = stations_df.filter(pl.col('station') == start).select(['lat', 'lon']).row(0)
        end_coords = stations_df.filter(pl.col('station') == end).select(['lat', 'lon']).row(0)        
        
        folium.GeoJson(
            distance_matrix_result["geometry"],
            color=color,
            weight=4,
            opacity=0.8
        ).add_to(m)        
        
        detailed_route.append({
            "start_point": start,
            "end_point": end            
        })
        
        station_type = stations_df.filter(pl.col('station') == start).select('type').item()
        num_bikes = complete_df.filter(pl.col('name') == start).select('num_bikes_available').item()
        capacity = complete_df.filter(pl.col('name') == start).select('capacity').item()                        
        
        popup_text, icon_color = create_marker_text_and_icon(start, num_bikes, capacity, station_type)                
            
        folium.Marker(
            location=start_coords,
            popup=popup_text,
            tooltip=i+1,
            icon=folium.Icon(color=icon_color, icon="info-sign")
        ).add_to(m)

        folium.Marker(
            location=start_coords,
            icon=folium.DivIcon(
                html=f'<div style="font-size: 16px; color: black; font-weight: bold; text-align: center;">{i+1}</div>'
            )
        ).add_to(m)

    last_station = optimized_path[-2]    
    last_coords = stations_df.filter(pl.col('station') == last_station).select(['lat', 'lon']).row(0)
    last_station_type = stations_df.filter(pl.col('station') == last_station).select('type').item()
    last_bikes = complete_df.filter(pl.col('name') == last_station).select('num_bikes_available').item()
    last_capacity = complete_df.filter(pl.col('name') == last_station).select('capacity').item()
    
    last_popup_text, last_icon_color = create_marker_text_and_icon(last_station, last_bikes, last_capacity, last_station_type)               
    
    folium.Marker(
        location=last_coords,
        popup=last_popup_text,
        tooltip=i+1,
        icon=folium.Icon(color=last_icon_color, icon="info-sign")
    ).add_to(m)
    
    plugins.MeasureControl(
        position='topleft',
        primary_length_unit='kilometers',
        secondary_length_unit='miles'
    ).add_to(m)

    
    optimized_route_info = {
        "total_distance_km": distance_matrix_result["distance"],
        "total_duration_min": distance_matrix_result["duration"],
        "detailed_route": detailed_route
    }
    
    return optimized_route_info, m


@st.cache_data(ttl=600,show_spinner=False)
def get_cached_map_one_route_html(mapa):
    return mapa

def show_map_static_one_route(mapa, filtro):
    
    map_html = get_cached_map_one_route_html(get_map_html(mapa) + filtro)
    st.components.v1.html(map_html, height=600)