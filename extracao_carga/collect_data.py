import streamlit as st
import requests
import pandas as pd
from datetime import datetime, timedelta
import time

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


#@st.cache_resource
def collect_data():
    
    station_information_list = []
    station_status_list = []
    
    for city, city_urls in urls.items():        
        station_information = fetch_data(city_urls["station_information"])
        station_information['city'] = city
        station_information['new_id'] = city + station_information['station_id']
        station_information_list.append(station_information)

        station_status = fetch_data(city_urls["station_status"])
        station_status['city'] = city
        station_status['new_id'] = city + station_status['station_id']
        station_status_list.append(station_status)
    
    all_station_information = pd.concat(station_information_list, ignore_index=True)
    all_station_status = pd.concat(station_status_list, ignore_index=True)    
    
    
    return all_station_information, all_station_status

