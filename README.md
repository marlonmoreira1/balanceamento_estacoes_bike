# Realocação de Bicicletas em Tempo Real do Sistema Tembici

A realocação de bicicletas é um desafio para o setor. Existem dois cenários críticos:

- **Estações vazias**, em que os usuários chegam e não encontram bicicletas para alugar.

- **Estações cheias**, em que as pessoas devolvem as bicicletas destrancadas e amontoadas, já que não há vagas disponíveis.

## Objetivo do Projeto

O objetivo do projeto é resolver o problema das estações vazias com o uso de dados. A ideia é simples: identificar as estações vazias e encontrar a estação mais próxima com bicicletas disponíveis para atuar como uma doadora, realocando-as de forma eficiente. Usando essa lógica, o processo se torna mais rápido e otimizado.

### 🏗 Arquitetura do Projeto

📥 **Coleta de Dados**

- Utilização do Google Cloud Functions + Cloud Scheduler para coletar os dados do GBFS a cada 10 minutos.

- Armazenamento dos dados no Google BigQuery (buffer para as consultas).

🔎 **Processamento dos Dados**

1. KDTree (SciPy) → Identifica os pares estação vazia ↔ estação cheia mais próximos com base na distância geográfica.

2. NetworkX (nx.algorithms) → Calcula a sequência ideal de redistribuição começando pela estação doadora.

3. OSRM (Open Source Routing Machine) → Gera a rota otimizada entre os pontos encontrados pelo NetworkX.

4. Folium → Plota a rota otimizada no mapa.

📊 Visualização e Alertas

- Streamlit → Aplicação interativa exibindo os pares de realocação e as rotas sugeridas.

- Slack → Envio de alerta caso uma estação permaneça vazia por mais de 5 horas.

- Armazenamento histórico → Dados antigos são movidos diariamente do BigQuery para o Azure SQL via GitHub Actions.

🛠 Tecnologias Utilizadas

- API: GBFS (Dados do sistema Tembici)

- Linguagem: Python

- Cloud: Google Cloud (Cloud Functions, Cloud Scheduler, BigQuery)

- Banco de Dados: BigQuery (dados temporários), Azure SQL (armazenamento histórico)

- Otimização de Rotas: KDTree (SciPy), NetworkX, OSRM

- App: Streamlit, Folium

- Automação: GitHub Actions

- Alertas: Slack API

## 🔗 Links
