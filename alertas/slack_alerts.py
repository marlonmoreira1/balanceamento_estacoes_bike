import pandas as pd
import os
from slack_sdk import WebClient
from tabulate import tabulate

def get_message(message):
    client = WebClient(token=os.environ["SLACK_TOKEN"])

    client.chat_postMessage(
        channel="alertas-de-vazias", 
        text=message, 
        username="Alerts"        
    )


def send_alert(df_vazia):

    vazias = df_vazia.groupby('city')[['name','groups','capacity']].apply(lambda x: x.reset_index(drop=True))

    for cidade, estacoes in vazias:
        estacoes_formatado = tabulate(estacoes, headers=['name','groups','capacity'],tablefmt='grid')
        message = f"Em {cidade.upper()}, estas estações estão no momento sem nenhuma bicicleta disponível:\n {estacoes_formatado}"
        get_message(message)

        
          
        
        



        
