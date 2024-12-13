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
        return get_valhalla(coords)

def get_valhalla(coords):

        if len(coords) <= 20:
            
            return request_valhalla(coords)
        else:
            
            chunk_size = 20
            total_distance = 0
            total_duration = 0
            all_geometry = []

            
            for i in range(0, len(coords), chunk_size):
                chunk = coords[i:i + chunk_size]
                result = request_valhalla(chunk)

                if result:
                    total_distance += result["distance"]
                    total_duration += result["duration"]
                    all_geometry.append(result["geometry"])

            consolidated_geometry = {
                "type": "LineString",
                "coordinates": [coord for geom in all_geometry for coord in geom["coordinates"]]
            }

            return {
                "distance": total_distance,
                "duration": total_duration,
                "geometry": consolidated_geometry
            }


def request_valhalla(coords):
    """
    Obtém a distância total, duração total e geometria para a rota entre os pontos usando Valhalla.
    Retorna no mesmo formato que o OSRM: distância (km), duração (minutos) e geometria (GeoJSON).
    """
    
    locations = [{"lat": lon, "lon": lat} for lon, lat in coords]
    
    url = "https://valhalla1.openstreetmap.de/route"  
    
    payload = {
        "locations": locations,
        "costing": "auto",
        "directions_options": {"units": "kilometers"}
    }

    try:
        
        response = requests.post(url, json=payload)
        response.raise_for_status()

        route = response.json()

        
        distance = route["trip"]["summary"]["length"]  
        duration = route["trip"]["summary"]["time"] / 60  
        geometry = route["trip"]["legs"][0]["shape"]

        
        
        decoded_coords = polyline.decode(geometry)  
        geojson_geometry = {
            "type": "LineString",
            "coordinates": [[lon, lat] for lat, lon in decoded_coords]
        }

        return {
            "distance": distance,
            "duration": duration,
            "geometry": geojson_geometry
        }

    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter rota com Valhalla: {e}")
        return None

