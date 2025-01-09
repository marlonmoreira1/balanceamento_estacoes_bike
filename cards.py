def create_card(status, count, color):    
    card_html = f""" 
    <div style=" 
        background-color: #f5f4f4; 
        padding: 4px 8px; 
        border-radius: 5px; 
        text-align: left; 
        margin-bottom: 25px; 
        box-shadow: 0 3px 5px rgba(0, 0, 0, 0.5);
        border-left: 15px solid {color};        
    "> 
        <div style="
            color: black;
            font-size: 1.5em;
            margin-bottom: 1px;
            text-transform: capitalize;
        ">
            {status}
        </div>
        <div style="
            font-size: 30px;
            color: black;
            font-weight: 500;
            margin-top: 0;
        ">
            {count}
        </div>
    </div> 
    """
    return card_html