def create_marker_text_and_icon(station, station_types):
    """
    Retorna o texto do popup e a cor do ícone com base no tipo da estação.
    """
    station_type = station_types[station]
    if station_type == "doadora":
        icon_color = "blue"
        popup_text = f"""
            <div style="font-family: Arial; padding: 5px;">
                <h4 style="margin: 0;">🔋 {station}</h4>
                <p style="margin: 5px 0;">Estação Doadora</p>
            </div>
        """
    else:
        icon_color = "red"
        popup_text = f"""
            <div style="font-family: Arial; padding: 5px;">
                <h4 style="margin: 0;">⚡ {station}</h4>
                <p style="margin: 5px 0;">Estação Vazia</p>
            </div>
        """
    return popup_text, icon_color