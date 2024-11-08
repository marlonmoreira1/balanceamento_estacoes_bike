import pandas as pd
import requests
import folium
import folium
from folium import plugins
from typing import Tuple
from typing import Dict, List, Tuple
import time
import random
from folium import plugins, FeatureGroup
import colorsys
from scipy.spatial import distance_matrix
import networkx as nx
from geopy.distance import geodesic
from rotas.cores_rotas import get_route, generate_distinct_colors


def optimize_routes_by_region(routes_info, max_distance_km=5):
    """
    Otimiza as rotas com base na proximidade regional das estações vazias e gera mapa interativo.
    """
    
    station_coords = {}
    empty_stations = set()
    donor_stations = set()
    
    
    for donor_name, info in routes_info.items():
        start_station = info["start_point"]["nearby_name"]
        start_coords = info["start_point"]["coords"]
        
        donor_stations.add(start_station)
        station_coords[start_station] = start_coords
        
        for dest in info["destinations"]:
            dest_name = dest["name"]
            dest_coords = dest["coords"]
            
            empty_stations.add(dest_name)
            station_coords[dest_name] = dest_coords

    
    empty_stations = list(empty_stations)
    
    
    empty_coords = [station_coords[station] for station in empty_stations]
    condensed_distance_matrix = []
    
    for i in range(len(empty_coords)):
        for j in range(i + 1, len(empty_coords)):
            distance = geodesic(empty_coords[i], empty_coords[j]).km
            condensed_distance_matrix.append(distance)

    
    Z = linkage(condensed_distance_matrix, method='single')
    region_labels = fcluster(Z, max_distance_km, criterion='distance')

    
    empty_stations_by_region = {}
    for i, region in enumerate(region_labels):
        if region not in empty_stations_by_region:
            empty_stations_by_region[region] = []
        empty_stations_by_region[region].append(empty_stations[i])

    
    all_coords = list(station_coords.values())
    center_lat = np.mean([coord[0] for coord in all_coords])
    center_lon = np.mean([coord[1] for coord in all_coords])
    m = folium.Map(location=[center_lat, center_lon], zoom_start=12)

    
    colors = generate_distinct_colors(len(empty_stations_by_region))
    color_map = dict(zip(empty_stations_by_region.keys(), colors))

    
    feature_groups = {region: FeatureGroup(name=f"Região {region}") 
                     for region in empty_stations_by_region.keys()}

    
    optimized_routes = []
    total_distance = 0
    
    for region, region_empty_stations in empty_stations_by_region.items():
        
        region_donors = set()
        for station in region_empty_stations:
            for donor_name, info in routes_info.items():
                if station in [dest["name"] for dest in info["destinations"]]:
                    region_donors.add(info["start_point"]["nearby_name"])
        
        region_donors = list(region_donors)
        
        
        G = nx.Graph()
        all_region_stations = region_empty_stations + region_donors
        
        
        for i, station1 in enumerate(all_region_stations):
            for station2 in all_region_stations[i+1:]:
                coord1 = station_coords[station1]
                coord2 = station_coords[station2]
                distance = geodesic(coord1, coord2).km
                G.add_edge(station1, station2, distance=distance)
        
        if len(G.edges) > 0:
            try:
                
                optimized_path = nx.algorithms.approximation.traveling_salesman_problem(G, weight="distance", cycle=False)
                region_distance = sum(G[optimized_path[i]][optimized_path[i+1]]["distance"] 
                                   for i in range(len(optimized_path) - 1))
                total_distance += region_distance
                
                
                optimized_route = []
                for i in range(len(optimized_path) - 1):
                    start = optimized_path[i]
                    end = optimized_path[i + 1]
                    start_coords = station_coords[start]
                    end_coords = station_coords[end]
                    
                    
                    route_details = get_route(start_coords, end_coords)
                    if route_details:
                        
                        route_html = f"""
                            <div>
                                <h4>📍 Rota - Região {region}</h4>
                                <p>De: {start}</p>
                                <p>Para: {end}</p>
                                <p>Distância: {round(route_details['distance'], 2)} km</p>
                                <p>Tempo estimado: {round(route_details['duration'], 2)} min</p>
                            </div>
                        """
                        
                        
                        folium.PolyLine(
                            locations=[[coord[1], coord[0]] for coord in route_details["geometry"]["coordinates"]],
                            weight=4,
                            color=color_map[region],
                            opacity=0.8,
                            popup=folium.Popup(route_html, max_width=300)
                        ).add_to(feature_groups[region])
                        
                        
                        for point, coords in [(start, start_coords), (end, end_coords)]:
                            icon_color = "green" if point in donor_stations else "red"
                            station_type = "Doadora" if point in donor_stations else "Vazia"
                            icon = "⚡" if point in donor_stations else "🔋"
                            
                            popup_text = f"""
                                <div>
                                    <h4>{icon} {point}</h4>
                                    <p>Estação {station_type}</p>
                                    <p>Região {region}</p>
                                </div>
                            """
                            
                            folium.Marker(
                                location=coords,
                                popup=popup_text,
                                icon=folium.Icon(color=icon_color, icon="info-sign")
                            ).add_to(feature_groups[region])
                        
                        optimized_route.append({
                            "start_point": start,
                            "end_point": end,
                            "distance_km": route_details["distance"],
                            "duration_min": route_details["duration"]
                        })
                
                optimized_routes.append({
                    "region": region,
                    "region_distance": round(region_distance, 2),
                    "optimized_route": optimized_route
                })
            except nx.NetworkXError:
                print(f"Não foi possível otimizar a rota para a região {region}")
        else:
            
            for empty_station in region_empty_stations:
                station_coords_point = station_coords[empty_station]
                
                
                popup_text = f"""
                    <div>
                        <h4>🔋 {empty_station}</h4>
                        <p>Estação Isolada</p>
                        <p>Região {region}</p>
                    </div>
                """
                
                folium.Marker(
                    location=station_coords_point,
                    popup=popup_text,
                    icon=folium.Icon(color="red", icon="info-sign")
                ).add_to(feature_groups[region])
                
                optimized_routes.append({
                    "region": region,
                    "region_distance": 0,
                    "optimized_route": [{
                        "start_point": empty_station,
                        "end_point": empty_station,
                        "distance_km": 0
                    }]
                })

    
    plugins.MeasureControl(
        position='topleft',
        primary_length_unit='kilometers',
        secondary_length_unit='miles'
    ).add_to(m)
    
    
    for group in feature_groups.values():
        group.add_to(m)
    folium.LayerControl().add_to(m)

    return {
        "total_distance": round(total_distance, 2),
        "optimized_routes": optimized_routes
    }, m
