import pandas as pd
import os
from slack_sdk import WebClient
from rotas.main_map import create_station_map
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def get_message(message):
    client = WebClient(token=os.environ["SLACK_TOKEN"])

    client.chat_postMessage(
        channel="alertas-de-vazias", 
        text=message, 
        username="Alerts"
    )

def send_file_to_slack(file_path, title):
    client = WebClient(token=os.environ["SLACK_TOKEN"])

    client.files_upload_v2(
        channels=os.environ["SLACK_CHANNEL_ID"], 
        file=file_path, 
        title=title,
        username="Alerts"
    )

def save_html_as_image(html_path, image_path):
    chrome_options = Options()
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--window-size=1920x1080")
    
   
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    driver.get(f"file://{os.path.abspath(html_path)}")
    driver.save_screenshot(image_path)  
    driver.quit()

def send_alert(df_vazia):

    vazias = df_vazia.groupby('city')[['name','groups','capacity']]

    for cidade, estacoes in vazias:
        #estacoes_formatado = estacoes.to_string(index=False)
        message = f"Em {cidade.upper()}, estas estações estão no momento sem nenhuma bicicleta disponível:\n {estacoes}"
        get_message(message)

        # mapa = create_station_map(df_vazia[df_vazia['city'] == cidade])
        # html_path = f"mapa_{cidade}.html"
        # image_path = f"mapa_{cidade}.png"

        # mapa.save(html_path)  
        # save_html_as_image(html_path, image_path)  
        
        # send_file_to_slack(image_path, title=f"Mapa de {cidade}")



        
