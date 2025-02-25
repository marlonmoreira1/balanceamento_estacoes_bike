import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account
import pandas as pd
from datetime import datetime, timedelta
import time
import os

credentials_info = {
  "type": st.secrets["TYPE"],
  "project_id": st.secrets["PROJECT_ID"],
  "private_key_id": st.secrets["PRIVATE_KEY_ID"],
  "private_key": st.secrets["PRIVATE_KEY"],
  "client_email": st.secrets["CLIENT_EMAIL"],
  "client_id": st.secrets["CLIENT_ID"],
  "auth_uri": st.secrets["AUTH_URI"],
  "token_uri": st.secrets["TOKEN_URI"],
  "auth_provider_x509_cert_url": st.secrets["AUTH_PROVIDER_X509_CERT_URL"],
  "client_x509_cert_url": st.secrets["CLIENT_X509_CERT_URL"],
  "universe_domain": st.secrets["UNIVERSE_DOMAIN"]
}    

credentials = service_account.Credentials.from_service_account_info(credentials_info)

client = bigquery.Client(credentials=credentials, project=credentials_info['project_id'])


@st.cache_data(ttl=550,show_spinner=False)
def consultar_dados_bigquery(consulta):
        query = consulta
        df = client.query(query).to_dataframe()    
        return df
