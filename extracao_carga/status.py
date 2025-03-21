import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import random
import json
import polars as pl
from scipy.spatial.distance import cdist
from scipy.spatial import KDTree
import os
from slack_sdk import WebClient
from tabulate import tabulate
from google.cloud import bigquery
from google.oauth2 import service_account
from dotenv import load_dotenv


urls = {
    "Salvador": {        
        "station_information": "https://salvador.publicbikesystem.net/customer/gbfs/v2/en/station_information",
        "station_status": "https://salvador.publicbikesystem.net/customer/gbfs/v2/en/station_status"
    },
    "Recife": {        
        "station_information": "https://rec.publicbikesystem.net/customer/gbfs/v2/en/station_information",
        "station_status": "https://rec.publicbikesystem.net/customer/gbfs/v2/en/station_status"
    },
    "São Paulo": {        
        "station_information": "https://saopaulo.publicbikesystem.net/customer/gbfs/v2/en/station_information",
        "station_status": "https://saopaulo.publicbikesystem.net/customer/gbfs/v2/en/station_status"
    },
    "Rio de Janeiro": {        
        "station_information": "https://riodejaneiro.publicbikesystem.net/customer/gbfs/v2/en/station_information",
        "station_status": "https://riodejaneiro.publicbikesystem.net/customer/gbfs/v2/en/station_status"
    },
    "Porto Alegre": {        
        "station_information": "https://poa.publicbikesystem.net/customer/gbfs/v2/en/station_information",
        "station_status": "https://poa.publicbikesystem.net/customer/gbfs/v2/en/station_status"
    }
}


def fetch_data(url):
    response = requests.get(url)    
    data = response.json().get("data")        
    if isinstance(data, dict) and len(data) == 1:
        data_key = list(data.keys())[0]
        return pd.DataFrame(data[data_key])
    else:
        return pd.DataFrame([data])
    return pd.DataFrame()


def collect_data(type):    
    
    station_list = []
    
    for city, city_urls in urls.items():

        station_status = fetch_data(city_urls[type])
        station_status['city'] = city
        station_status['new_id'] = city + station_status['station_id']
        station_list.append(station_status)    
    
    all_station = pd.concat(station_list, ignore_index=True)    
    
    return  all_station

def fill_group(row,df):    
    if row['groups']==None and not row['groups_nearby']==None:
        return row['groups_nearby']
    elif row['groups']==None and row['groups_nearby']==None:
        candidate = df.loc[~df['groups_nearby'].isna(), 'groups_nearby'].iloc[0]
        return candidate
    return row['groups']


def get_regions(row):
        if isinstance(row['groups'],list) and len(row['groups'])>0:
            return row['groups'][0]
        return None 


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
                'new_id': row['new_id'],
                'station_id': row['station_id'],
                'name': row['name'],
                'address': row['address'],
                'lat': row['lat'],
                'lon': row['lon'],            
                'groups': row['groups'],
                'data': row['data'],
                'last_reported': row['last_reported'],
                'nearby_new_id': nearby['new_id'],
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


def get_message(message):
    client = WebClient(token=os.environ["SLACK_TOKEN"],timeout=30)

    client.chat_postMessage(
        channel="alertas-de-vazias", 
        text=message, 
        username="Alerts"        
    )

def send_alert(df_vazia):    

    vazias = df_vazia.groupby('city')[['name','groups','capacity']]    

    for cidade, estacoes in vazias:
        estacoes_formatado = tabulate(estacoes, headers=['name','groups','capacity'],tablefmt='grid',showindex=False)
        message = f"Na {cidade.upper()} estas estações estão no momento sem nenhuma bicicleta disponível:\n {estacoes_formatado}"

        get_message(message)

@functions_framework.http
def main(request):

    load_dotenv()    

    status_data = collect_data("station_status")

    information_data = collect_data("station_information")

    status_data['last_reported'] = pd.to_datetime(status_data['last_reported'], unit='s')

    selected_columns_information = information_data[['new_id', 'name', 'physical_configuration', 'lat', 'lon', 'altitude', 'address', 'capacity', 'is_charging_station', 'groups']]
    selected_columns_status = status_data[['new_id', 'station_id', 'num_bikes_available', 'num_bikes_disabled', 'num_docks_available', 'num_docks_disabled', 'last_reported', 'status','city']]

    df_merged = pd.merge(
    selected_columns_status,
    selected_columns_information,
    on='new_id',
    how='left'
)

    df_merged['station_type_situation'] = df_merged.apply(station_type,axis=1)

    df_merged['data'] = df_merged['last_reported']

    df_merged['groups'] = df_merged.apply(get_regions,axis=1)

    doadora = df_merged.loc[(df_merged['num_bikes_available']>6)&\
                        (df_merged['status']=='IN_SERVICE'),\
                   ['new_id','station_id','num_bikes_available','name','lat','lon','address',
                   'station_type_situation','last_reported','capacity','status','groups','data']]


    vazias = df_merged.loc[(df_merged['num_bikes_available']<1)&\
                       (df_merged['status']=='IN_SERVICE'),\
                   ['new_id','station_id','num_bikes_available','name','lat','lon','address',
                   'station_type_situation','last_reported','capacity','status','groups','data']]

    vazia_doadora_par = get_par(doadora,vazias)

    alerta = vazias[['new_id', 'num_bikes_available',
'station_type_situation','last_reported', 'name', 'groups', 'capacity', 'data']]

    par = vazia_doadora_par[['new_id', 'station_id','name','nearby_new_id', 'nearby_station_id','name_nearby','last_reported','data']]

    status = df_merged[[
    'new_id', 
    'station_id',  
    'num_bikes_available',
    'num_bikes_disabled',  
    'num_docks_available',
    'num_docks_disabled',  
    'last_reported',
    'status',  
    'city',  
    'name',  
    'physical_configuration',  
    'lat', 
    'lon', 
    'altitude', 
    'address',  
    'capacity', 
    'groups', 
    'station_type_situation',
    'data'  
]]


    credentials_json = os.environ["GOOGLE_CREDENTIALS"]

    credentials_info = json.loads(credentials_json)    

    credentials = service_account.Credentials.from_service_account_info(credentials_info)

    client = bigquery.Client(credentials=credentials, project=credentials_info['project_id'])

    status_table_id = os.environ["TABLE_ID"]

    def consultar_dados_bigquery(consulta):
        query = consulta
        df = client.query(query).to_dataframe()    
        return df

    status_job_config = bigquery.LoadJobConfig(  
        
        schema = [
        bigquery.SchemaField("new_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("station_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("num_bikes_available", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("num_bikes_disabled", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("num_docks_available", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("num_docks_disabled", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("last_reported", "DATETIME", mode="NULLABLE"),
        bigquery.SchemaField("status", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("city", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("physical_configuration", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("lat", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("lon", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("altitude", "FLOAT", mode="NULLABLE"),
        bigquery.SchemaField("address", "STRING", mode="NULLABLE"),        
        bigquery.SchemaField("capacity", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("groups", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("station_type_situation", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("data", "DATE", mode="NULLABLE")       
    ],
        
        write_disposition="WRITE_APPEND"
    )

    job_status = client.load_table_from_dataframe(
        status, status_table_id, job_config=status_job_config
    )  
    job_status.result()  

    table = client.get_table(status_table_id)  
    print(
        "Loaded {} rows and {} columns to {}".format(
            table.num_rows, len(table.schema), status_table_id
        )
    )   


    par_table_id = os.environ["TABLE_ID_PAR"]

    par_job_config = bigquery.LoadJobConfig(  
        
        schema = [
        bigquery.SchemaField("new_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("station_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("nearby_new_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("nearby_station_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("name_nearby", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("last_reported", "DATETIME", mode="NULLABLE"),
        bigquery.SchemaField("data", "DATE", mode="NULLABLE")       
    ],
        
        write_disposition="WRITE_APPEND"
    )

    job_par = client.load_table_from_dataframe(
        par, par_table_id, job_config=par_job_config
    )  
    job_par.result()  

    table = client.get_table(par_table_id)  
    print(
        "Loaded {} rows and {} columns to {}".format(
            table.num_rows, len(table.schema), par_table_id
        )
    )



    alerta_table_id = os.environ["TABLE_ID_ALERTA"]

    alerta_job_config = bigquery.LoadJobConfig(  
        
        schema = [
        bigquery.SchemaField("new_id", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("num_bikes_available", "INTEGER", mode="NULLABLE"),
        bigquery.SchemaField("station_type_situation", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("last_reported", "DATETIME", mode="NULLABLE"),
        bigquery.SchemaField("name", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("groups", "STRING", mode="NULLABLE"),
        bigquery.SchemaField("capacity", "INTEGER", mode="NULLABLE"),       
        bigquery.SchemaField("data", "DATE", mode="NULLABLE")       
    ],
        
        write_disposition="WRITE_APPEND"
    )

    job_alerta = client.load_table_from_dataframe(
        alerta, alerta_table_id, job_config=alerta_job_config
    )  
    job_alerta.result()  

    table = client.get_table(alerta_table_id)  
    print(
        "Loaded {} rows and {} columns to {}".format(
            table.num_rows, len(table.schema), alerta_table_id
        )
    )


    dados_alerta = consultar_dados_bigquery("""    
    WITH Controle_Alerta AS (
       SELECT 
       new_id
       FROM 
       bike-balancing.bike_data.alerta
       WHERE
       _PARTITIONTIME >= TIMESTAMP(DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 390 MINUTE))
       AND new_id IN (
              SELECT 
              new_id              
              FROM 
              bike-balancing.bike_data.alerta
              WHERE 
              _PARTITIONTIME >= TIMESTAMP(DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 380 MINUTE))
              GROUP BY 
              new_id
              HAVING 
              COUNT(new_id) = 36
       )
       GROUP BY 
       new_id
       HAVING 
       COUNT(new_id) = 36
),

Contagem_Linhas AS (
       SELECT 
       new_id,
       name,
      `groups`,  
       capacity,
       last_reported,
       ROW_NUMBER() OVER (PARTITION BY name ORDER BY last_reported) AS ranking     
       FROM 
       bike-balancing.bike_data.alerta
       WHERE
       _PARTITIONTIME >= TIMESTAMP(DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 380 MINUTE))
       ORDER BY 6 DESC
)

SELECT
l.new_id,
l.name,
l.groups,
l.capacity,
l.last_reported
FROM
Controle_Alerta c
JOIN 
Contagem_Linhas l
ON
c.new_id = l.new_id
WHERE
l.last_reported >= DATETIME_SUB(CURRENT_DATETIME(), INTERVAL 10 MINUTE)
AND l.ranking = 36;
    """)

    dados_alerta['city'] = dados_alerta['new_id'].str.extract(r'([^\d]+)')

    send_alert(dados_alerta)
    return 'Processo completo!'

if __name__ == "__main__":
    main()