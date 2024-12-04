import pandas as pd
from typing import Dict, List, Tuple
import time
import random
from folium import plugins, FeatureGroup
from scipy.spatial import KDTree
from scipy.spatial.distance import cdist

def get_par(doadoras,vazias):
    coords_vazias = vazias[['lat', 'lon']].values
    coords_doadoras = doadoras[['lat', 'lon']].values    
    
    tree = KDTree(coords_doadoras)
    
    resultados = []
    
    for _, row in vazias.iterrows():  
        station_id = row['station_id']
        lat, lon = row['lat'], row['lon']
        
        
        dist, idx = tree.query([lat, lon], k=1)  
        nearby_station_id = doadoras.iloc[idx]['station_id']        
        
        nearby_data = doadoras.iloc[idx]
        
        resultados.append({
            'station_id': station_id,
            'name': row['name'],
            'address': row['address'],
            'lat': lat,
            'lon': lon,
            "groups": row['groups'],
            'nearby_station_id': nearby_station_id,
            'distance': dist,
            'address_nearby': nearby_data['address'],
            'name_nearby': nearby_data['name'],
            'lat_nearby': nearby_data['lat'],
            'lon_nearby': nearby_data['lon'],
            'status': nearby_data['status'],
            'num_bikes_available': nearby_data['num_bikes_available'],
            'capacity': nearby_data['capacity']
        })
    
    vazia_doadora_par = pd.DataFrame(resultados)
    return vazia_doadora_par