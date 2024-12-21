import pandas as pd
import streamlit as st

def get_new_stations(novos_dados):    
    
    if st.session_state.historico_requisicoes:
        combinado_df = pd.concat(st.session_state.historico_requisicoes, ignore_index=True)   
        ultimo_ids = set(combinado_df['new_id'])  
    else:
        ultimo_ids = set()
    
    novos_ids = set(novos_dados['new_id'])
    novas_estacoes_ids = novos_ids - ultimo_ids
    
    novas_estacoes_df = novos_dados[novos_dados['new_id'].isin(novas_estacoes_ids)]
        
    
    return novas_estacoes_df,ultimo_ids