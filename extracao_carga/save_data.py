import pandas as pd
from azure.storage.blob import BlobServiceClient
from datetime import datetime, timedelta
import os


def salvar_no_blob(pilha, pasta,container):
    
    blob_service_client = BlobServiceClient.from_connection_string(os.environ["CONNECTION_STRING"])
    container_client = blob_service_client.get_container_client(container)

    df_completo = pd.concat(pilha, ignore_index=True)
    nome_arquivo = f"{pasta}/dados_{datetime.now().strftime('%H%M%S')}.parquet"
    df_completo.to_parquet("temp.parquet", index=False)    
    
    with open("temp.parquet", "rb") as data:
        container_client.upload_blob(name=nome_arquivo, data=data, overwrite=True)    

def atualizar_pilha(df, pilha, pasta,container):
    pilha.append(df)
    if len(pilha) == 3:  
        salvar_no_blob(pilha, pasta,container)
        pilha.clear()
