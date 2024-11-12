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
from streamlit_autorefresh import st_autorefresh
from rotas.one_route import optimize_complete_route_with_map, show_map_static_one_route
from rotas.regions_routes import optimize_routes_by_region
from rotas.main_map import show_map_static, create_station_map
from pares.find_par import get_par
from calculate_routes.distance_routes import calculate_station_routes
from extracao_carga.collect_data import collect_data

st_autorefresh(interval=150000, key="refresh_key")

all_station_information, all_station_status = collect_data()

all_station_status['last_reported'] = pd.to_datetime(all_station_status['last_reported'], unit='s')


selected_columns_information = all_station_information[['new_id', 'name', 'physical_configuration', 'lat', 'lon', 'altitude', 'address', 'capacity', 'is_charging_station', 'groups']]
selected_columns_status = all_station_status[['new_id', 'station_id', 'num_bikes_available', 'num_bikes_disabled', 'num_docks_available', 'num_docks_disabled', 'last_reported', 'status','city']]


df_merged = pd.merge(
    selected_columns_status,
    selected_columns_information,
    on='new_id',
    how='left'
)


city = st.selectbox("Cidade: ",df_merged['city'].unique(),key=1)

df_merged = df_merged[df_merged['city']==city]

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


vazia_doadora_par = get_par(df_merged,vazias)

df_filter = vazia_doadora_par[vazia_doadora_par['nearby_station_id'].isin(doadora['station_id'])]

df_agrupado = df_filter.groupby('station_id').head(2)
df_route3 = df_filter.groupby('station_id').head(3)

final_df = df_agrupado.loc[df_agrupado.groupby('station_id')['num_bikes_available'].idxmax()]

route_max = final_df.groupby('nearby_station_id').apply(lambda x: x.reset_index(drop=True)).reset_index(drop=True)
route_closer = df_filter.groupby('station_id').head(1)

st.title("Mapa das Estações e Conexões")

mapa_principal = create_station_map(df_merged, df_agrupado)

show_map_static(mapa_principal,filtro=city)

one_route = calculate_station_routes(route_max)

one_route_optmized, mapa_one_route = optimize_complete_route_with_map(one_route)

show_map_static_one_route(mapa_one_route,filtro=city)

st.write("Distância total da rota otimizada:", one_route_optmized["total_distance_km"], "km")
st.write("Tempo total da rota otimizada:", one_route_optmized["total_duration_min"], "minutos")
st.write("Rota otimizada:")
for step in one_route_optmized["detailed_route"]:
    st.write(f"De {step['start_point']} para {step['end_point']}, Distância: {step['distance_km']} km")


st.dataframe(df_merged[['station_id', 'num_bikes_available', 'last_reported', 'status','city']])

