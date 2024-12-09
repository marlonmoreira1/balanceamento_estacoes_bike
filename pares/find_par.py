import pandas as pd
from typing import Dict, List, Tuple
import time
import random
from folium import plugins, FeatureGroup
from scipy.spatial import KDTree
from scipy.spatial.distance import cdist

def fill_group(row):
    if row['groups']==None:
        return row['groups_nearby']
    return row['groups']

def get_par(doadoras, vazias):
    coords_vazias = vazias[['lat', 'lon']].values
    coords_doadoras = doadoras[['lat', 'lon']].values    

    tree = KDTree(coords_doadoras)

    resultados = []

    for _, row in vazias.iterrows():
        station_id = row['station_id']
        lat, lon = row['lat'], row['lon']

        
        dist, idx = tree.query([lat, lon], k=2)

        
        for i in range(len(idx)):
            nearby_data = doadoras.iloc[idx[i]]
            resultados.append({
                'station_id': station_id,
                'name': row['name'],
                'address': row['address'],
                'lat': lat,
                'lon': lon,
                "groups": row['groups'],
                'nearby_station_id': nearby_data['station_id'],
                'distance': dist[i],
                'address_nearby': nearby_data['address'],
                'name_nearby': nearby_data['name'],
                'lat_nearby': nearby_data['lat'],
                'lon_nearby': nearby_data['lon'],
                'groups_nearby':nearby_data['groups'],
                'status': nearby_data['status'],
                'num_bikes_available': nearby_data['num_bikes_available'],
                'capacity': nearby_data['capacity']
            })

    vazia_doadora_par = pd.DataFrame(resultados)
    vazia_doadora_par['groups'] = vazia_doadora_par.apply(fill_group,axis=1) 
    return vazia_doadora_par
