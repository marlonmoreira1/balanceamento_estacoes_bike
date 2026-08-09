# Realocação de Bicicletas em Tempo Real do Sistema Tembici

## Impacto Potencial e Benefícios da Solução
Este projeto propõe uma solução analítica para o problema de estações vazias no sistema de bicicletas compartilhadas da Tembici.

🔍 **Impacto estimado:** A análise mostra que, em média, as estações permanecem **2h30 sem bicicletas disponíveis** nos horários de pico.
Com a aplicação do algoritmo de redistribuição otimizada, seria possível **reduzir esse tempo para cerca de 1h**, otimizando a operação e **aumentando em até 60% a disponibilidade de bicicletas em áreas críticas**.

🚨 Estações que permanecem vazias por longos períodos são identificadas e alertadas automaticamente via Slack, permitindo atuação proativa da equipe operacional.

[APP](https://equilibici.streamlit.app/)

## Resumo do Projeto
Provavelmente você já viu ou até usou as bicicletas do Itaú (ou de outras marcas como Estácio, Claro, dependendo da cidade) que fazem parte do sistema Tembici. A gestão desses sistemas apresenta desafios complexos.
Entre eles está a logística de compartilhamento de bicicletas que visa garantir que os usuários sempre encontrem bicicletas disponíveis para aluguel e tenham vagas para devolução. No entanto, dois cenários críticos ocorrem com frequência:

- **Estações vazias**, em que os usuários chegam e não encontram bicicletas para alugar.

- **Estações cheias**, em que as pessoas devolvem as bicicletas destrancadas e amontoadas, já que não há vagas disponíveis.

[Artigo Medium Parte 1](https://medium.com/p/6dd4a3b772f2)

## Objetivo do Projeto

O objetivo do projeto é resolver o problema das estações vazias com o uso de dados. A ideia é simples: identificar as estações vazias e encontrar a estação mais próxima com bicicletas disponíveis para atuar como uma doadora, realocando-as de forma eficiente. Usando essa lógica, o processo se torna mais rápido e otimizado.
Vale ressaltar que, em alguns casos, o projeto pode acabar ajudando a aliviar também o segundo problema (estações cheias), já que essas estações podem atuar como doadoras. No entanto, esse não é o objetivo do projeto.

## Fonte dos Dados
GBFS (General Bikeshare Feed Specification), um padrão aberto usado para disponibilizar informações de sistemas de bicicletas compartilhadas em tempo real. No projeto, utilizo os dados do GBFS referentes às cidades do Brasil que fazem parte do sistema Tembici. Ele permite acessar dados como disponibilidade de bicicletas e status das estações, o que tornou possível estruturar o projeto. Inicialmente, o projeto foi pensado apenas para Salvador, minha cidade, mas ao descobrir que o GBFS também tinha dados de outras cidades do Brasil dentro do Tembici, resolvi incluí-las também.

### 🏗 Arquitetura do Projeto

📥 **Coleta de Dados**

- Utilização do Google Cloud Functions + Cloud Scheduler para coletar os dados do GBFS a cada 10 minutos.

- Armazenamento dos dados no Google BigQuery (buffer para as consultas).

🔎 **Processamento dos Dados**

1. KDTree (SciPy) → Identifica os pares estação vazia ↔ estação doadora mais próximos com base na distância geográfica.

2. NetworkX (nx.algorithms) → Calcula a sequência ideal de redistribuição começando pela estação doadora.

3. OSRM (Open Source Routing Machine) → Gera a rota otimizada entre os pontos encontrados pelo NetworkX.

4. Folium → Plota a rota otimizada no mapa.

📊 Visualização e Alertas

- Streamlit → Aplicação interativa exibindo os pares de realocação e as rotas sugeridas.

- Slack → Envio de alerta caso uma estação permaneça vazia por mais de 5 horas.

- Armazenamento histórico → Dados são movidos diariamente do BigQuery para o Azure SQL via GitHub Actions.

🛠 Tecnologias Utilizadas

- API: GBFS (Dados do sistema Tembici)

- Linguagem: Python

- Cloud: Google Cloud (Cloud Functions, Cloud Scheduler, BigQuery) e Azure (Azure SQL)

- Banco de Dados: BigQuery (dados temporários), Azure SQL (armazenamento histórico e permanente)

- Otimização de Rotas: KDTree (SciPy), NetworkX, OSRM

- App: Streamlit, Folium

- Automação: GitHub Actions

- Alertas: Slack API

![Arquitetura do Projeto](https://github.com/user-attachments/assets/4393a11f-daf5-4c12-9229-4027f02ea1f5)

## 🔗 Links

[Artigo Medium Parte 2](https://medium.com/p/59b1e195938e)

[Artigo Medium Parte 3](https://medium.com/p/1e950685f357)

[Artigo Medium Parte 4](https://medium.com/p/0f7e5178b0d6)

[Artigo Medium Parte 5](https://medium.com/p/e56ec7b2db12)

[Artigo Medium Parte 6](https://medium.com/p/2e0b3be48d1e)
