def create_marker_text_and_icon(station, num_bike, capacity, station_type):
    """
    Retorna o texto do popup e a cor do ícone com base no tipo da estação.
    """
    
    if station_type == "doadora":
        icon_color = "blue"
        popup_text = f"""
            <div style="font-family: Arial; padding: 5px;">
                <h4 style="margin: 0;">🔋 {station}</h4>
                <p style="margin: 5px 0;">Estação Doadora</p>
                <p style="margin: 5px 0;">Disponibilidade/Capacidade: {num_bike}/{capacity}</p>                                             
            </div>
        """
    else:
        icon_color = "red"
        popup_text = f"""
            <div style="font-family: Arial; padding: 5px;">
                <h4 style="margin: 0;">⚡ {station}</h4>
                <p style="margin: 5px 0;">Estação Vazia</p>
                <p style="margin: 5px 0;">Disponibilidade/Capacidade: {num_bike}/{capacity}</p>                                                
            </div>
        """
    return popup_text, icon_color