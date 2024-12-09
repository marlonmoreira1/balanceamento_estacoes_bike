import pandas as pd
import requests
import time
import random
import streamlit as st
import plotly.express as px
from dotenv import load_dotenv
from streamlit_autorefresh import st_autorefresh
from rotas.one_route import optimize_complete_route_with_map, show_map_static_one_route
from rotas.regions_routes import optimize_routes_by_region, show_map_static_region_route
from rotas.main_map import show_map_static, create_station_map
from pares.find_par import get_par
from calculate_routes.distance_routes import calculate_station_routes
from extracao_carga.collect_data import collect_data
from alertas.slack_alerts import send_alert

#st_autorefresh(interval=90000, key="refresh_key")
inicio = time.time()
all_station_information, all_station_status = collect_data()
fim = time.time()
st.write(fim-inicio)
inicio = time.time()
all_station_status['last_reported'] = pd.to_datetime(all_station_status['last_reported'], unit='s')


selected_columns_information = all_station_information[['new_id', 'name', 'physical_configuration', 'lat', 'lon', 'altitude', 'address', 'capacity', 'is_charging_station', 'groups']]
selected_columns_status = all_station_status[['new_id', 'station_id', 'num_bikes_available', 'num_bikes_disabled', 'num_docks_available', 'num_docks_disabled', 'last_reported', 'status','city']]


df_merged = pd.merge(
    selected_columns_status,
    selected_columns_information,
    on='new_id',
    how='left'
)

def get_regions(row):
        if isinstance(row['groups'],list) and len(row['groups'])>0:
            return row['groups'][0]
        return None  

df_merged['groups'] = df_merged.apply(get_regions,axis=1) 

city = st.selectbox("Cidade: ",df_merged['city'].unique(),key=1)

df_filtered = df_merged[df_merged['city']==city]

num_ssa_rec_rio = 9
num_poa_sp = 6

n = {
    "Salvador": num_ssa_rec_rio,
    "Recife": num_ssa_rec_rio,
    "São Paulo": num_poa_sp,
    "Rio de Janeiro": num_ssa_rec_rio,
    "Porto Alegre": num_poa_sp
}

def station_type(row):

    if row['num_bikes_available']<1 and row['status']=='IN_SERVICE':
        return 'vazia'

    elif row['num_bikes_available']>n[city] and row['status']=='IN_SERVICE':
        return 'doadora'

    elif (row['num_bikes_available']>0 and row['num_bikes_available']<=3) and row['status']=='IN_SERVICE':
        return 'risco'

    return 'normal'


df_filtered['station_type_situation'] = df_filtered.apply(station_type,axis=1)

doadora = df_filtered.loc[(df_filtered['num_bikes_available']>n[city])&\
                        (df_filtered['status']=='IN_SERVICE'),\
                   ['station_id','num_bikes_available','name','lat','lon','address','capacity','status','groups']]


vazias = df_filtered.loc[(df_filtered['num_bikes_available']<1)&\
                       (df_filtered['status']=='IN_SERVICE'),\
                   ['station_id','num_bikes_available','name','lat','lon','address','capacity','status','groups']]
fim = time.time()
st.write(fim-inicio)
inicio = time.time()
vazia_doadora_par = get_par(doadora,vazias)

df_filter = vazia_doadora_par[vazia_doadora_par['nearby_station_id'].isin(doadora['station_id'])]

df_agrupado = df_filter.groupby('station_id').head(2)

final_df = df_agrupado.loc[df_agrupado.groupby('station_id')['num_bikes_available'].idxmax()]

num_ssa_rec_rio = 2
num_poa_sp = 5

route_max = final_df.groupby('nearby_station_id').apply(lambda x: x.reset_index(drop=True)).reset_index(drop=True)

route_closer = df_filter.groupby('station_id').head(n[city])
fim = time.time()
st.write(fim-inicio)
inicio = time.time()
st.title("Mapa das Estações e Conexões")

mapa_principal = create_station_map(df_filtered)

show_map_static(mapa_principal,filtro=city)
fim = time.time()
st.write(fim-inicio)
inicio = time.time()


one_route_optmized, map_one_route = optimize_complete_route_with_map(route_closer)

show_map_static_one_route(map_one_route,filtro=city)

st.write("Distância total da rota otimizada:", one_route_optmized["total_distance_km"], "km")
st.write("Tempo total da rota otimizada:", one_route_optmized["total_duration_min"], "minutos")
st.write("Rota otimizada:")
for step in one_route_optmized["detailed_route"]:
    st.write(f"De {step['start_point']} para {step['end_point']}")
fim = time.time()
st.write(fim-inicio)
inicio = time.time()
regions_optimized, map_regions_route = optimize_routes_by_region(route_closer)
show_map_static_region_route(map_regions_route,filtro=city)
fim = time.time()
st.write(fim-inicio)


load_dotenv()
vazias_alerta = df_merged.loc[(df_merged['num_bikes_available']<1)&\
                       (df_merged['status']=='IN_SERVICE'),\
                   ['station_id','num_bikes_available','name','lat',
                   'lon','address','capacity','status','groups','city']]

vazias_alerta['station_type_situation'] = vazias_alerta.apply(station_type,axis=1)

send_alert(vazias_alerta)