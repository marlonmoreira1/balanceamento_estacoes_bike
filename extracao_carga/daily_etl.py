import os
import pandas as pd
from datetime import datetime, timedelta
import time
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.exc import DBAPIError
import pyodbc
import urllib.parse
import json
from google.cloud import bigquery
from google.oauth2 import service_account


credentials_json = os.environ["GOOGLE_CREDENTIALS"]

credentials_info = json.loads(credentials_json)

credentials = service_account.Credentials.from_service_account_info(credentials_info)

client = bigquery.Client(credentials=credentials, project=credentials_info['project_id'])

def consultar_dados_bigquery(consulta):
    query = consulta
    df = client.query(query).to_dataframe()    
    return df
 

def conectar_azure_sql():

    params = urllib.parse.quote_plus(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        f'SERVER={os.environ["SERVER"]};'
        f'DATABASE={os.environ["DATABASE"]};'
        f'UID={os.environ["UID"]};'
        f'PWD={os.environ["PWD"]}'                
    )
    
    connection_string = f'mssql+pyodbc:///?odbc_connect={params}'

    max_retries = 10
    attempt = 0
    engine = None

    while attempt < max_retries:
        try:
            engine = create_engine(
                connection_string, 
                fast_executemany=True, 
                connect_args={"timeout": 60}  
            )
            
            @event.listens_for(engine, "before_cursor_execute")
            def receive_before_cursor_execute(conn, cursor, statement, params, context, executemany):
                if executemany:
                    cursor.fast_executemany = True

            with engine.connect() as conn:
                conn.execute(text("SELECT voo FROM [dbo].[Teste]"))                
                          
            
            print(f"Conexão estabelecida com sucesso na tentativa {attempt + 1}")
            return engine
            
        except (DBAPIError, pyodbc.Error) as e:  
            print(f"Tentativa {attempt + 1} falhou: {str(e)}")
            
            
            if "40613" in str(e):
                print("Erro 40613: Banco temporariamente indisponível")
                time.sleep(30)  
            else:
                time.sleep(10)
                
            attempt += 1
    
    raise Exception("Falha ao conectar ao Azure SQL Server após várias tentativas.")  


def main():    
    
    engine = conectar_azure_sql()
    
    
    dados_status = consultar_dados_bigquery("""    
    SELECT
    new_id,
    num_bikes_available,
    num_docks_available,
    last_reported,
    station_type_situation,
    data
    FROM
    `bike-balancing.bike_data.status`
    WHERE
    DATE(_PARTITIONTIME) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
    """)

    dados_par = consultar_dados_bigquery("""    
    SELECT
    *
    FROM
    `bike-balancing.bike_data.par`
    WHERE
    DATE(_PARTITIONTIME) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
    """)

    dados_alerta = consultar_dados_bigquery("""    
    SELECT
    *
    FROM
    `bike-balancing.bike_data.alerta`
    WHERE
    DATE(_PARTITIONTIME) = DATE_SUB(CURRENT_DATE(), INTERVAL 1 DAY)
    """)


    dados_status.to_sql(
        name='BikeStations',  
        con=engine,
        index=False,
        if_exists="append",  
        schema="dbo"  
    )


    dados_par.to_sql(
        name='ParStations',  
        con=engine,
        index=False,
        if_exists="append",  
        schema="dbo"  
    )

    dados_alerta.to_sql(
        name='Alerts',  
        con=engine,
        index=False,
        if_exists="append",  
        schema="dbo"  
    )
    
    

if __name__ == '__main__':
    main()