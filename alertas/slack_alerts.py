import pandas as pd
import streamlit as st
import os
import datetime
import time
from slack_sdk import WebClient
from tabulate import tabulate

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
        message = f"{cidade.upper()}, estas estações estão no momento sem nenhuma bicicleta disponível há 3 horas:\n {estacoes_formatado}"

        get_message(message)
            

        
          
        
        



        
