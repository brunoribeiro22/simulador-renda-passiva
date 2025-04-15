import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="Central de Renda Passiva", layout="wide")

st.title("🏦 Central Inteligente de Renda Passiva com Ações da B3")

# Entradas
st.sidebar.header("⚙️ Configurações")
aporte_mensal = st.sidebar.number_input("Aporte Mensal (R$)", min_value=0, value=2000, step=100)
investimento_inicial = st.sidebar.number_input("Investimento Inicial (R$)", min_value=0, value=10000, step=100)
dy_anual = st.sidebar.slider("Dividend Yield Anual Estimado (%)", 0.0, 20.0, 8.0, 0.1)
dy_mensal = dy_anual / 100 / 12

# Carteira fixa
carteira = {
    'BBAS3': 100,
    'HAPV3': 200,
    'JHSF3': 500,
    'KLBN4': 220,
    'VALE3': 50,
    'RBRR11': 1,
    'RZTR11': 12
}

st.sidebar.markdown("---")
st.sidebar.write("Carteira Atual:")
for ativo, qtd in carteira.items():
    st.sidebar.write(f"{ativo}: {qtd} ações/cotas")

# Função de busca
@st.cache_data(show_spinner=False)
def buscar_indicadores(ticker):
    try:
        acao = yf.Ticker(ticker + ".SA")
        info = acao.info
        return {
            "Empresa": info.get("longName", "-"),
            "Setor": info.get("sector", "-"),
            "Preço Atual": info.get("currentPrice", 0),
            "P/L": info.get("trailingPE", 0),
            "Dividend Yield (%)": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else 0,
            "ROE": info.get("returnOnEquity", 0)
        }
    except:
        return {
            "Empresa": ticker,
            "Setor": "-",
            "Preço Atual": 0,
            "P/L": 0,
            "Dividend Yield (%)": 0,
            "ROE": 0
        }

st.subheader("📊 Análise da Carteira Atual")
dados_analise = []
for ativo, qtd in carteira.items():
    dados = buscar_indicadores(ativo)
    dados["Ticker"] = ativo
    dados["Quantidade"] = qtd
    dados_analise.append(dados)

df_analise = pd.DataFrame(dados_analise)
st.dataframe(df_analise.set_index("Ticker"))

# Radar de Oportunidades
st.subheader("🧲 Radar de Oportunidades por Dividendos")
ativos_recomendados = ["TAEE11", "TRPL4", "EGIE3", "ITSA4", "BBDC4", "CPLE6", "BBAS3", "SAPR11", "MXRF11", "HGLG11"]
ranking = []

for papel in ativos_recomendados:
    info = buscar_indicadores(papel)
    if info['Dividend Yield (%)'] >= 6 and info['P/L'] and info['P/L'] < 15:
        score = info['Dividend Yield (%)'] + (info['ROE'] or 0) - info['P/L']
        info['Score'] = round(score, 2)
        info['Ticker'] = papel
        ranking.append(info)

df_ranking = pd.DataFrame(ranking).sort_values(by="Score", ascending=False)
st.dataframe(df_ranking.set_index("Ticker"))

# Simulação
st.subheader("📈 Projeção de Renda Passiva")
metas = [100, 1000, 10000]
capital_total = investimento_inicial
renda_mensal = capital_total * dy_mensal
progresso = []
mes = 0

while renda_mensal < metas[-1]:
    renda_mensal = capital_total * dy_mensal
    mes += 1
    capital_total += renda_mensal + aporte_mensal
    for meta in metas:
        if renda_mensal >= meta and meta not in [m['Meta'] for m in progresso]:
            progresso.append({"Meta": f"R$ {meta}/mês", "Meses": mes, "Anos": round(mes / 12, 1)})

df_metas = pd.DataFrame(progresso)
st.table(df_metas)

# Gráfico
st.subheader("📉 Evolução do Capital com Reinvestimentos")
capital = investimento_inicial
hist_capital = []
for i in range(mes):
    capital += capital * dy_mensal + aporte_mensal
    hist_capital.append(capital)
st.line_chart(hist_capital)

# Calendário de Dividendos Mensais (modelo baseado em histórico)
st.subheader("📅 Mapeamento de Dividendos Mensais")
calendario = {
    "Jan": ["BBAS3", "TAEE11"],
    "Fev": ["MXRF11", "ITSA4"],
    "Mar": ["SAPR11", "HGLG11"],
    "Abr": ["EGIE3", "BBDC4"],
    "Mai": ["TRPL4"],
    "Jun": ["ITSA4", "RZTR11"],
    "Jul": ["BBAS3", "CPLE6"],
    "Ago": ["MXRF11", "TAEE11"],
    "Set": ["ITUB4", "HGLG11"],
    "Out": ["TAEE11", "EGIE3"],
    "Nov": ["SAPR11"],
    "Dez": ["BBAS3", "MXRF11"]
}
df_calendario = pd.DataFrame.from_dict(calendario, orient="index").reset_index()
df_calendario.columns = ["Mês", "Ativo 1", "Ativo 2"]
st.dataframe(df_calendario)

st.caption("App automatizado com base em dados reais para montar uma carteira de dividendos contínuos.")
