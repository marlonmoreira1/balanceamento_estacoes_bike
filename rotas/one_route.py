import pandas as pd
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


@st.cache_data(show_spinner=False)
def optimize_complete_route_with_map(df_stations):
    """
    Otimiza a rota para cobrir todas as estações (doadoras e vazias) em uma única rota,
    obtém as rotas detalhadas entre as estações na sequência otimizada e plota no mapa.

    Parameters:
    df_stations (pd.DataFrame): DataFrame contendo informações das estações e suas distâncias.

    Returns:
    dict: Dicionário com informações da rota otimizada.
    folium.Map: Mapa Folium com a rota otimizada visualizada.
    """
        
    G = nx.Graph()    
    
    all_stations = {}
    station_types = {}    
    
    
    for _, row in df_stations.iterrows():
        start_station = row['name_nearby']
        start_coords = (row['lat_nearby'], row['lon_nearby'])
        all_stations[start_station] = start_coords

        donor_station = row['name']
        donor_coords = (row['lat'], row['lon'])
        all_stations[donor_station] = donor_coords

        station_types[row['name_nearby']] = "doadora"
        station_types[row['name']] = "vazia"        


        for station1, coords1 in all_stations.items():
            for station2, coords2 in all_stations.items():
                if station1 != station2:
                    distance = geodesic(coords1, coords2).km
                    if station_types[station1] == 'vazia' and station_types[station2] == 'vazia':
                        distance *= 5 
                    G.add_edge(station1, station2, distance=distance)      
        
    
    optimized_path = nx.algorithms.approximation.traveling_salesman.christofides(G, weight="distance")    

    start_coords = all_stations[optimized_path[0]]
    m = folium.Map(location=[start_coords[0], start_coords[1]], zoom_start=12)

    color = "blue"
    
    total_distance = 0
    total_duration = 0
    detailed_route = []
    
    optimized_coords = [all_stations[station] for station in optimized_path]
    
    distance_matrix_result = get_distance_matrix(optimized_coords)
    
    for i in range(len(optimized_path)-1):
        start = optimized_path[i]
        end = optimized_path[i+1]
        
        start_coords = all_stations[start]
        end_coords = all_stations[end]        
        
        folium.GeoJson(
            distance_matrix_result["geometry"],
            color=color,
            weight=4,
            opacity=0.8
        ).add_to(m)        
        
        detailed_route.append({
            "start_point": start,
            "end_point": end,
            "distance_km": distance_matrix_result["distance"],
            "duration_min": distance_matrix_result["duration"]
        })
        
        station_type = station_types[start]        
        
        popup_text, icon_color = create_marker_text_and_icon(start, station_types)
                
            
        folium.Marker(
            location=start_coords,
            popup=popup_text,
            tooltip=i+1,
            icon=folium.Icon(color=icon_color, icon="info-sign")
        ).add_to(m)

    last_station = optimized_path[-2]    
    last_coords = all_stations[last_station]
    station_type = station_types[last_station]
    last_popup_text, last_icon_color = create_marker_text_and_icon(last_station, station_types)               
    
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
        "total_distance_km": total_distance,
        "total_duration_min": total_duration,
        "detailed_route": detailed_route
    }
    
    return optimized_route_info, m


@st.cache_data(show_spinner=False)
def get_cached_map_one_route_html(mapa):
    return mapa

def show_map_static_one_route(mapa, filtro):
    
    map_html = get_cached_map_one_route_html(get_map_html(mapa) + filtro)
    st.components.v1.html(map_html, height=600)