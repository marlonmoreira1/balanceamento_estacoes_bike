# Use uma imagem oficial do Python 3.9 como base
FROM python:3.9-slim

# Defina o diretório de trabalho dentro do contêiner
WORKDIR /bike_sharing_real_time

# Copie o arquivo requirements.txt para o contêiner
COPY requirements.txt /bike_sharing_real_time/

# Instale as dependências do requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copie todo o restante do código do seu app para o contêiner
COPY . /bike_sharing_real_time/

# Exponha a porta que o Streamlit vai usar (padrão 8501)
EXPOSE 8501

# Defina a variável de ambiente para não exibir a interface no navegador
ENV STREAMLIT_SERVER_HEADLESS=true

# Comando para rodar o Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501"]
