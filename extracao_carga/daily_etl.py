import os
import pandas as pd
from datetime import datetime, timedelta
from io import BytesIO
import time
from azure.storage.blob import BlobServiceClient
import pyodbc
from dotenv import load_dotenv
from collect_data import collect_data

load_dotenv()
BLOB_CONNECTION_STRING = os.environ["CONNECTION_STRING"]
CONTAINER_NAME = os.environ["CONTAINER_NAME"]


def get_regions(row):
        if isinstance(row['groups'],list) and len(row['groups'])>0:
            return row['groups'][0]
        return None  


def consolidar_e_enviar_sql(container):
    
    data_anterior = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    pasta_anterior = f"{data_anterior}/"  
    
    
    blob_service_client = BlobServiceClient.from_connection_string(BLOB_CONNECTION_STRING)
    container_client = blob_service_client.get_container_client(container)
    
    
    blobs = container_client.list_blobs(name_starts_with=pasta_anterior)
    arquivos_parquet = [blob.name for blob in blobs if blob.name.endswith(".parquet")]    
    
    dataframes = []
    for arquivo in arquivos_parquet:
        blob_client = container_client.get_blob_client(arquivo)
        
        
        stream = blob_client.download_blob().readall()
        df = pd.read_parquet(BytesIO(stream))
        dataframes.append(df)
    
    
    if dataframes:
        df_final = pd.concat(dataframes, ignore_index=True)
    else:
        df_final = pd.DataFrame()  
    
    return df_final
    


def inserir_sql(conn,container,table_name):
    df = consolidar_e_enviar_sql(container)
    
    df = df.dropna(subset=['last_reported'])

    cursor = conn.cursor()

    colunas_formatadas = ', '.join([f'[{col}]' for col in df.columns])    
    placeholders = ', '.join(['?'] * len(df.columns))    
    
    insert_query = f"INSERT INTO [dbo].[{table_name}] ({colunas_formatadas}) VALUES ({placeholders})"
    cursor.executemany(insert_query, df.values.tolist())
    conn.commit()

def conectar_azure_sql():
    credentials = (
    'Driver={ODBC Driver 17 for SQL Server};'
    f'Server={os.environ["SERVER"]};'
    f'Database={os.environ["DATABASE"]};'
    f'Uid={os.environ["UID"]};'
    f'Pwd={os.environ["PWD"]}'
)

    max_retries = 3
    attempt = 0
    connected = False

    while attempt < max_retries and not connected:
        try:
            conn = pyodbc.connect(credentials,timeout=20)		
            connected = True
        except pyodbc.Error as e:
            print(f"Connection attempt {attempt + 1} failed: {e}")
            attempt += 1
            time.sleep(10)
    
    return conn

def carregar_no_sql(df, table_name, conn):    
    cursor = conn.cursor()

    
    colunas_formatadas = ', '.join([f'[{col}]' for col in df.columns])
    placeholders = ', '.join(['?'] * len(df.columns))
    
    
    insert_query = f"INSERT INTO [dbo].[{table_name}] ({colunas_formatadas}) VALUES ({placeholders})"

    
    cursor.execute(f"DELETE FROM [dbo].[{table_name}]")
    print(f"Dados apagados da tabela {table_name}.")

    
    cursor.executemany(insert_query, df.values.tolist())
    conn.commit()
    print(f"Dados inseridos na tabela {table_name} com sucesso.")   
    


def main():
    
    conn = conectar_azure_sql()
    
    # df_information = collect_data("station_information")

    # df_information = df_information[['new_id', 'station_id', 'name', 'physical_configuration', 'lat', 'lon', 'address', 'capacity', 'groups']]

    # df_information['groups'] = df_information.apply(get_regions,axis=1)

    # df_status = collect_data("station_status")

    # df_status = df_status[['new_id', 'num_bikes_disabled', 'num_docks_disabled', 'status','city']]    

    # df_information = df_information.fillna('')

    # df_status = df_status.fillna('')

    # carregar_no_sql(df_status,os.environ['TS'],conn)

    # carregar_no_sql(df_information,os.environ['TI'],conn)    

    inserir_sql(conn,os.environ['CN'],os.environ['TN'])

    inserir_sql(conn,CONTAINER_NAME,os.environ['TSR'])    
    
    conn.close()

if __name__ == '__main__':
    main()