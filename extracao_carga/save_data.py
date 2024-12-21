import pandas as pd
from io import BytesIO
import streamlit as st
from azure.storage.blob import BlobServiceClient
from datetime import datetime, timedelta
import os


def salvar_no_blob(pilha, pasta,container):
    
    blob_service_client = BlobServiceClient.from_connection_string(st.secrets["CONNECTION_STRING"])
    container_client = blob_service_client.get_container_client(container)

    df_completo = pd.concat(pilha, ignore_index=True).drop_duplicates()
    nome_arquivo = f"{pasta}/dados_{datetime.now().strftime('%H%M%S')}.parquet"
    
    buffer = BytesIO()
    df_completo.to_parquet(buffer, index=False)
    buffer.seek(0)    
    
    container_client.upload_blob(name=nome_arquivo, data=buffer, overwrite=True)   

def atualizar_pilha(pilha, pasta,container):    
    if len(st.session_state.pilha) == 50:  
        salvar_no_blob(pilha, pasta,container)                
