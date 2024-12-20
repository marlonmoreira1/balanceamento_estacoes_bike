import pandas as pd

def get_new_stations(novos_dados, historico_requisicoes):    
    
    if historico_requisicoes:
        combinado_df = pd.concat(historico_requisicoes, ignore_index=True)   
        ultimo_ids = set(combinado_df['station_id'])  
    else:
        ultimo_ids = set()
    
    novos_ids = set(novos_dados['station_id'])
    novas_estacoes_ids = novos_ids - ultimo_ids
    
    novas_estacoes_df = novos_dados[novos_dados['station_id'].isin(novas_estacoes_ids)]
    historico_requisicoes.append(novos_dados)

    return novas_estacoes_df