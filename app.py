import pandas as pd
import requests
import folium
from typing import Dict, List, Tuple
import time
import random
from folium import plugins, FeatureGroup
import colorsys
from scipy.spatial import distance_matrix
import networkx as nx
from geopy.distance import geodesic
import streamlit as st
from streamlit_folium import st_folium
import plotly.express as px
from rotas.one_route import optimize_complete_route_with_map
from rotas.regions_routes import optimize_routes_by_region
from rotas.main_map import show_map_static

urls = {
    "vehicle_types": "https://salvador.publicbikesystem.net/customer/gbfs/v2/en/vehicle_types",
    "station_information": "https://salvador.publicbikesystem.net/customer/gbfs/v2/en/station_information",
    "station_status": "https://salvador.publicbikesystem.net/customer/gbfs/v2/en/station_status"
}


def fetch_data(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json().get("data")
        if data:
            
            if isinstance(data, dict) and len(data) == 1:
                data_key = list(data.keys())[0]
                return pd.DataFrame(data[data_key])
            else:
                return pd.DataFrame([data])
    return pd.DataFrame()  


df_vehicle_types = fetch_data(urls["vehicle_types"])
df_station_information = fetch_data(urls["station_information"])
df_station_status = fetch_data(urls["station_status"])


df_station_status['last_reported'] = pd.to_datetime(df_station_status['last_reported'], unit='s')


df_merged = pd.merge(
    df_station_status,
    df_station_information,
    on='station_id',
    how='left'  
)

def station_type(row):

    if row['num_bikes_available']<1 and row['status']=='IN_SERVICE':
        return 'vazia'
    elif row['num_bikes_available']>12 and row['status']=='IN_SERVICE':
        return 'doadora'
    elif (row['num_bikes_available']>0 and row['num_bikes_available']<=3) and row['status']=='IN_SERVICE':
        return 'risco'
    return 'normal'


df_merged['station_type_situation'] = df_merged.apply(station_type,axis=1)

doadora = df_merged.loc[(df_merged['num_bikes_available']>12)&\
                        (df_merged['status']=='IN_SERVICE'),\
                   ['station_id','num_bikes_available','name','lat','lon','address','capacity','status']]


vazias = df_merged.loc[(df_merged['num_bikes_available']<1)&\
                       (df_merged['status']=='IN_SERVICE'),\
                   ['station_id','num_bikes_available','name','lat','lon','address','capacity','status']]



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

df_filter = vazia_doadora_par[vazia_doadora_par['nearby_station_id'].isin(doadora['station_id'])]

df_agrupado = df_filter.groupby('station_id').head(2)
df_route3 = df_filter.groupby('station_id').head(3)

final_df = df_agrupado.loc[df_agrupado.groupby('station_id')['num_bikes_available'].idxmax()]

route_max = final_df.groupby('nearby_station_id').apply(lambda x: x.reset_index(drop=True)).reset_index(drop=True)
route_closer = df_filter.groupby('station_id').head(1)

st.title("Mapa das Estações e Conexões")


show_map_static(df_merged, route_closer)