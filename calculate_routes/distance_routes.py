import pandas as pd
import requests
import folium
from typing import Dict, List, Tuple
import time
import random
from rotas.cores_rotas import get_route
from concurrent.futures import ThreadPoolExecutor

def calculate_station_routes(df_routes):
    
    routes_info = {}
    donors = df_routes['name_nearby'].unique()

    def process_donor(donor_name):
        donor_routes = df_routes[df_routes['name_nearby'] == donor_name]
        donor_info = {
            "start_point": {
                "nearby_name": donor_name,
                "coords": (donor_routes.iloc[0]['lat_nearby'], donor_routes.iloc[0]['lon_nearby'])
            },
            "destinations": []
        }

        for _, row in donor_routes.iterrows():
            start_coords = (row['lat_nearby'], row['lon_nearby'])
            end_coords = (row['lat'], row['lon'])
            route = get_route(start_coords, end_coords)
            if route:
                donor_info["destinations"].append({
                    "name": row['name'],
                    "coords": end_coords,
                    "distance_km": round(route["distance"], 2),
                    "duration_min": round(route["duration"], 2)
                })
        return donor_name, donor_info

    with ThreadPoolExecutor(max_workers=10) as executor:
        results = executor.map(process_donor, donors)
        for donor_name, donor_info in results:
            routes_info[donor_name] = donor_info

    return routes_info
