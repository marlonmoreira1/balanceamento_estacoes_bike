import pandas as pd
import requests
import folium
import folium
from folium import plugins
from typing import Tuple
from typing import Dict, List, Tuple
import time
import streamlit as st
import random
from folium import plugins, FeatureGroup
import colorsys
from scipy.spatial import distance_matrix
import networkx as nx
from geopy.distance import geodesic
from rotas.cores_rotas import get_route, generate_distinct_colors
from rotas.main_map import get_map_html


def optimize_complete_route_with_map(routes_info):
    """
    Otimiza a rota para cobrir todas as estações (doadoras e vazias) em uma única rota,
    obtém as rotas detalhadas entre as estações na sequência otimizada e plota no mapa.

    Parameters:
    routes_info (dict): Dicionário com informações das rotas entre estações doadoras e vazias.

    Returns:
    dict: Dicionário com informações da rota otimizada.
    folium.Map: Mapa Folium com a rota otimizada visualizada.
    """
    
    
    G = nx.Graph()
    
    
    all_stations = {}
    station_types = {}  
    for donor_name, info in routes_info.items():
        
        start_station = info["start_point"]["nearby_name"]
        start_coords = info["start_point"]["coords"]
        all_stations[start_station] = start_coords
        station_types[start_station] = "doadora"
        
       
        for dest in info["destinations"]:
            dest_station = dest["name"]
            dest_coords = dest["coords"]
            all_stations[dest_station] = dest_coords
            station_types[dest_station] = "vazia"
    
    
    for station1, coords1 in all_stations.items():
        for station2, coords2 in all_stations.items():
            if station1 != station2:
                distance = geodesic(coords1, coords2).km
                G.add_edge(station1, station2, distance=distance)
    
    
    optimized_path = nx.algorithms.approximation.traveling_salesman.christofides(G, weight="distance")
    
    
    start_coords = all_stations[optimized_path[0]]
    m = folium.Map(location=[start_coords[0], start_coords[1]], zoom_start=12)

    
    color = "blue"
    
   
    total_distance = 0
    total_duration = 0
    detailed_route = []

    for i in range(len(optimized_path) - 2):  
        start = optimized_path[i]
        end = optimized_path[i + 1]
        
        start_coords = all_stations[start]
        end_coords = all_stations[end]
        
        
        route_info = get_route(start_coords, end_coords)
        
        if route_info:
            total_distance += route_info["distance"]
            total_duration += route_info["duration"]
            
            
            folium.GeoJson(
                route_info["geometry"],
                style_function=lambda x: {"color": color, "weight": 4, "opacity": 0.8}
            ).add_to(m)
            
            
            detailed_route.append({
                "start_point": start,
                "end_point": end,
                "distance_km": route_info["distance"],
                "duration_min": route_info["duration"]
            })

            
            station_type = station_types.get(start, "vazia")  
            if station_type == "doadora":
                icon_color = "green"
                popup_text = f"""
                    <div style="font-family: Arial; padding: 5px;">
                        <h4 style="margin: 0;">🔋 {start}</h4>
                        <p style="margin: 5px 0;">Estação Doadora</p>
                    </div>
                """
            else:
                icon_color = "red"
                popup_text = f"""
                    <div style="font-family: Arial; padding: 5px;">
                        <h4 style="margin: 0;">⚡ {start}</h4>
                        <p style="margin: 5px 0;">Estação Vazia</p>
                    </div>
                """
                
            
            folium.Marker(
                location=start_coords,
                popup=popup_text,
                icon=folium.Icon(color=icon_color, icon="info-sign")
            ).add_to(m)
               
    
    folium.Marker(
        location=end_coords,
        popup=popup_text,
        icon=folium.Icon(color=icon_color, icon="info-sign")
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

def show_map_oneroute(mapa):   
  
    @st.cache_data(show_spinner=False)
    def get_cached_map_html(_mapa):
        
        return get_map_html(_mapa)
    
   
    map_html = get_cached_map_html(mapa)
    
    
    st.components.v1.html(map_html, height=600)