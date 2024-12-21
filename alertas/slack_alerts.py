import pandas as pd
import streamlit as st
import os
import datetime
from slack_sdk import WebClient
from slack_bolt import App
from tabulate import tabulate

def get_message(message):
    client = App(token=st.secrets["SLACK_TOKEN"])

    client.chat_postMessage(
        channel="alertas-de-vazias", 
        text=message, 
        username="Alerts"        
    )


def send_alert(df_vazia):

    if df_vazia.empty:
        return
    
    timestamp = datetime.datetime.now()

    vazias = df_vazia.groupby('city')[['name','groups','capacity']]
    if len(st.session_state.alerts):
        alerts_filtro = st.session_state.alerts[-1]

    for cidade, estacoes in vazias:
        estacoes_formatado = tabulate(estacoes, headers=['name','groups','capacity'],tablefmt='grid',showindex=False)
        message = f"Na {cidade.upper()},e hora = {timestamp}; estas estações estão no momento sem nenhuma bicicleta disponível:\n {estacoes_formatado}"

        if len(alerts_filtro)>0:
            get_message(message)

        
          
        
        



        
