import pandas as pd
import numpy as np
import requests
import folium
from typing import Dict, List, Tuple
import time
import random
import streamlit as st
from folium import plugins, FeatureGroup
import colorsys
from scipy.spatial import distance_matrix
from scipy.cluster.hierarchy import linkage, fcluster
import networkx as nx
from geopy.distance import geodesic
from rotas.cores_rotas import get_route, generate_distinct_colors
from calculate_routes.distance_matrix import get_distance_matrix
from rotas.main_map import get_map_html


def optimize_routes_by_region(df_stations):
    """
    Otimiza rotas para cada região, criando rotas separadas para cada grupo de estações.

    Parameters:
    df_stations (pd.DataFrame): DataFrame contendo informações das estações, incluindo grupos/regiões.

    Returns:
    dict: Dicionário contendo informações de rotas otimizadas por região.
    folium.Map: Um único mapa com todas as rotas.
    """
    
    regional_routes = {}
    colors = ["blue", "red", "green", "purple", "orange", "darkred", "darkblue", "darkgreen"]
    
    start_coords = (df_stations['lat'].iloc[0], df_stations['lon'].iloc[0])
    m = folium.Map(location=start_coords, zoom_start=12)

    feature_groups = {region: folium.FeatureGroup(name=f"Região {region}") for region in df_stations['groups'].unique()}

    for idx, region in enumerate(df_stations['groups'].unique()):
        df_region = df_stations[df_stations['groups'] == region]
        
        if df_region.empty:
            continue
        
        color = colors[idx % len(colors)]  
        
        G = nx.Graph()
        all_stations = {}
        station_types = {}
        
        for _, row in df_region.iterrows():
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
                        G.add_edge(station1, station2, distance=distance)
        
        if len(all_stations) > 1:
            
            optimized_path = nx.algorithms.approximation.traveling_salesman.christofides(G, weight="distance")
                        
            detailed_route = []
            optimized_coords = [all_stations[station] for station in optimized_path]
                        
            distance_matrix_result = get_distance_matrix(optimized_coords)
            
            
            for i, station in enumerate(optimized_path):
                coords = all_stations[station]
                
                station_type = station_types[station]
                icon_color = "blue" if station_type == "doadora" else "red"
                
                popup_text = f"""
                    <div style="font-family: Arial; padding: 5px;">
                        <h4 style="margin: 0;">{'🔋' if station_type == 'doadora' else '⚡'} {station}</h4>
                        <p style="margin: 5px 0;">Estação {station_type.capitalize()}</p>
                        <p style="margin: 5px 0;">Região: {region}</p>
                    </div>
                """
                
                folium.Marker(
                    location=coords,
                    popup=popup_text,
                    tooltip=i,
                    icon=folium.Icon(color=icon_color, icon="info-sign")
                ).add_to(feature_groups[region])
                
                
                next_station = optimized_path[i]
                next_coords = all_stations[next_station]
                
                folium.GeoJson(
                    distance_matrix_result["geometry"],
                    color=color,
                    weight=4,
                    opacity=0.8
                ).add_to(feature_groups[region])
                    
                    
                detailed_route.append({
                    "start_point": station,
                    "end_point": next_station,
                    "distance_km": distance_matrix_result["distance"],
                    "duration_min": distance_matrix_result["duration"]
                })
            
            regional_routes[region] = {
                "total_stations": len(all_stations),
                "stations": list(all_stations.keys()),
                "detailed_route": detailed_route
            }
    

    for group in feature_groups.values():
        group.add_to(m)
    folium.LayerControl().add_to(m)
    
    return regional_routes, m



@st.cache_data(show_spinner=False)
def get_cached_map_region_route_html(mapa):
    return mapa


def show_map_static_region_route(mapa, filtro):
    
    map_html = get_cached_map_region_route_html(get_map_html(mapa) + filtro)
    st.components.v1.html(map_html, height=600)