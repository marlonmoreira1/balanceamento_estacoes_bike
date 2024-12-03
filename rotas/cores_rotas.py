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


def get_route(start_coords: Tuple[float, float], end_coords: Tuple[float, float]) -> dict:
    """Obtém rota entre dois pontos com cache para melhorar performance."""
    url = f"http://router.project-osrm.org/route/v1/driving/{start_coords[1]},{start_coords[0]};{end_coords[1]},{end_coords[0]}?overview=full&geometries=geojson"
    try:
        response = requests.get(url)
        
        route = response.json()
        
        return {
            "distance": route["routes"][0]["distance"] / 1000,
            "duration": route["routes"][0]["duration"] / 60,
            "geometry": route["routes"][0]["geometry"]
        }
    except requests.exceptions.RequestException:
        pass
    return None



def generate_distinct_colors(n):
    """Gera n cores visualmente distintas"""
    colors = []
    for i in range(n):
        hue = i / n
        sat = 0.9
        val = 0.9
        rgb = colorsys.hsv_to_rgb(hue, sat, val)
        color = '#{:02x}{:02x}{:02x}'.format(
            int(rgb[0] * 255),
            int(rgb[1] * 255),
            int(rgb[2] * 255)
        )
        colors.append(color)
    return colors


