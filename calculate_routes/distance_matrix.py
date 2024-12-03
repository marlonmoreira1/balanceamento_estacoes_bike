import requests

def get_distance_matrix(coords):
    """
    Obtém a distância total, duração total e geometria para a rota entre os pontos usando OSRM.
    """
    coord_string = ";".join([f"{lon},{lat}" for lat, lon in coords])  
    url = f"http://router.project-osrm.org/route/v1/driving/{coord_string}?overview=full&geometries=geojson"
    
    try:
        response = requests.get(url)
        response.raise_for_status()  
        
        route = response.json()
        return {
            "distance": route["routes"][0]["distance"] / 1000,  
            "duration": route["routes"][0]["duration"] / 60,    
            "geometry": route["routes"][0]["geometry"]          
        }
    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter rota: {e}")
        return None
