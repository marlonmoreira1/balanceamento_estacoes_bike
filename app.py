import pandas as pd
import requests
from datetime import datetime, timedelta
import time
import random
import streamlit as st
from streamlit_autorefresh import st_autorefresh
from rotas.one_route import optimize_complete_route_with_map, show_map_static_one_route
from rotas.regions_routes import optimize_routes_by_region, show_map_static_region_route
from rotas.main_map import show_map_static, create_station_map
from pares.find_par import get_par
from calculate_routes.distance_routes import calculate_station_routes
from extracao_carga.collect_data import collect_data


st.set_page_config(page_title='Interesses',layout='wide')

st_autorefresh(interval=120000, key="refresh_key")

inicio = time.time()
all_station_status = collect_data("station_status")
all_station_information = collect_data("station_information")
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

def station_type(row):

    if row['num_bikes_available']<1 and row['status']=='IN_SERVICE':
        return 'vazia'

    elif row['num_bikes_available']>6 and row['status']=='IN_SERVICE':
        return 'doadora'

    elif (row['num_bikes_available']>0 and row['num_bikes_available']<=3) and row['status']=='IN_SERVICE':
        return 'risco'

    elif row['status'] != 'IN_SERVICE':
        return 'indisponivel'

    return 'normal'


df_filtered['station_type_situation'] = df_filtered.apply(station_type,axis=1)

doadora = df_filtered.loc[(df_filtered['num_bikes_available']>6)&\
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

df_merged['station_type_situation'] = df_merged.apply(station_type,axis=1)

num_ssa_rec_rio = 2
num_poa = 2
num_sp = 2

n = {
    "Salvador": num_ssa_rec_rio,
    "Recife": num_ssa_rec_rio,
    "São Paulo": num_poa,
    "Rio de Janeiro": num_ssa_rec_rio,
    "Porto Alegre": num_sp
}

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
regions_optimized, map_regions_route = optimize_routes_by_region(route_closer,df_merged)
show_map_static_region_route(map_regions_route,filtro=city)

st.subheader("Sumário por Região")
cols = st.columns(len(regions_optimized))
for col, (regiao, info) in zip(cols, regions_optimized.items()):
    with col:
        st.metric(
            label=f"Região {regiao}",
            value=f"{round(info['distance_km'], 1)} km",
            delta=f"{round(info['duration_min'], 1)} min",
            delta_color="off"
        )
fim = time.time()
st.write(fim-inicio)

inicio = time.time()

one_route_optmized, map_one_route = optimize_complete_route_with_map(route_closer,df_merged)

show_map_static_one_route(map_one_route,filtro=city)

col1, col2 = st.columns(2)
with col1:
    st.metric(
        label="Distância Total da Rota",
        value=f"{round(one_route_optmized['total_distance_km'], 1)} km"
    )
with col2:
    st.metric(
        label="Tempo Total da Rota",
        value=f"{round(one_route_optmized['total_duration_min'], 1)} min"
    )


with st.expander("Ver Detalhes da Rota", expanded=True):
    for step in one_route_optmized["detailed_route"]:
        st.write(f"🚗 {step['start_point']} ➡️ {step['end_point']}")
fim = time.time()
st.write(fim-inicio)



