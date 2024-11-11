import pandas as pd
from typing import Dict, List, Tuple
import time
import random
from folium import plugins, FeatureGroup
from scipy.spatial import distance_matrix



def get_par(df_merged,vazias):
    coords = df_merged[['lat', 'lon']].values
    dist_matrix = distance_matrix(coords, coords)  


    dist_df = pd.DataFrame(dist_matrix, index=df_merged['station_id'], columns=df_merged['station_id'])


    resultados = []


    for station_id in vazias['station_id']:
        proximas = dist_df[station_id].sort_values()[1:]  
        for nearby_station_id in proximas.index[:30]:  
            
            name = df_merged.loc[df_merged['station_id'] == station_id, 'name'].values[0]
            address = df_merged.loc[df_merged['station_id'] == station_id, 'address'].values[0]
            lat = df_merged.loc[df_merged['station_id'] == station_id, 'lat'].values[0]
            lon = df_merged.loc[df_merged['station_id'] == station_id, 'lon'].values[0]
            
            distancia = proximas[nearby_station_id]  
            num_bikes_available = df_merged.loc[df_merged['station_id'] == nearby_station_id, 'num_bikes_available'].values[0]
            capacity = df_merged.loc[df_merged['station_id'] == nearby_station_id, 'capacity'].values[0]
            address_nearby = df_merged.loc[df_merged['station_id'] == nearby_station_id, 'address'].values[0]
            name_nearby = df_merged.loc[df_merged['station_id'] == nearby_station_id, 'name'].values[0]
            lat_nearby = df_merged.loc[df_merged['station_id'] == nearby_station_id, 'lat'].values[0]
            lon_nearby = df_merged.loc[df_merged['station_id'] == nearby_station_id, 'lon'].values[0]
            status = df_merged.loc[df_merged['station_id'] == nearby_station_id, 'status'].values[0]
            
            resultados.append({
                'station_id': station_id,
                'name': name,
                'address': address,
                'lat': lat,
                'lon': lon,
                'nearby_station_id': nearby_station_id,
                'distance': distancia,
                'address_nearby': address_nearby,
                'name_nearby': name_nearby,
                'lat_nearby': lat_nearby,
                'lon_nearby': lon_nearby,
                'status': status,
                'num_bikes_available': num_bikes_available,
                'capacity': capacity
            })

    vazia_doadora_par = pd.DataFrame(resultados)

    return vazia_doadora_par