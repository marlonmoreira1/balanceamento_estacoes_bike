import pandas as pd
import polars as pl
from typing import Dict, List, Tuple
import time
import random
from folium import plugins, FeatureGroup
from scipy.spatial import KDTree
from scipy.spatial.distance import cdist

def fill_group(row,df):    
    if row['groups']==None and not row['groups_nearby']==None:
        return row['groups_nearby']
    elif row['groups']==None and row['groups_nearby']==None:
        candidate = df.loc[~df['groups_nearby'].isna(), 'groups_nearby'].iloc[0]
        return candidate
    return row['groups']


def get_par(doadoras, vazias):
    coords_vazias = vazias[['lat', 'lon']].values
    coords_doadoras = doadoras[['lat', 'lon']].values    

    tree = KDTree(coords_doadoras)
    distancias, indices = tree.query(coords_vazias, k=2)

    resultados = []
    doadoras_pl = pl.from_pandas(doadoras)
    vazias_pl = pl.from_pandas(vazias)

    for i, row in enumerate(vazias_pl.iter_rows(named=True)):
        nearest_indices = indices[i]
        nearest_distances = distancias[i]

        for j, idx in enumerate(nearest_indices):
            nearby = doadoras_pl.row(idx, named=True)
            resultados.append({
                'station_id': row['station_id'],
                'name': row['name'],
                'address': row['address'],
                'lat': row['lat'],
                'lon': row['lon'],            
                'groups': row['groups'],
                'nearby_station_id': nearby['station_id'],
                'distance': nearest_distances[j],
                'address_nearby': nearby['address'],
                'name_nearby': nearby['name'],
                'lat_nearby': nearby['lat'],
                'lon_nearby': nearby['lon'],
                'groups_nearby':nearby['groups'],
                'status': nearby['status'],
                'num_bikes_available': nearby['num_bikes_available'],
                'capacity': nearby['capacity']
            })

    vazia_doadora_par = pd.DataFrame(resultados)    
    vazia_doadora_par['groups'] = vazia_doadora_par.apply(lambda row: fill_group(row, vazia_doadora_par), axis=1) 
    return vazia_doadora_par
