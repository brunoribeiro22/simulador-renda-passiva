
import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Simulador e Analisador de Renda Passiva", layout="wide")

st.title("📊 Simulador e Analisador de Renda Passiva com Ações da B3")

# Entradas do simulador
st.sidebar.header("Configurações da Simulação")
aporte_mensal = st.sidebar.number_input("Aporte mensal (R$)", min_value=0, value=2000, step=100)
investimento_inicial = st.sidebar.number_input("Investimento inicial (R$)", min_value=0, value=10000, step=100)
dy_anual = st.sidebar.slider("Dividend Yield anual estimado (%)", min_value=0.0, max_value=20.0, value=8.0, step=0.1)

# Carteira inicial (pode ser expandida com input do usuário futuramente)
st.sidebar.header("Carteira Atual")
carteira = {
    'BBAS3': 100,
    'HAPV3': 200,
    'JHSF3': 500,
    'KLBN4': 220,
    'VALE3': 50,
    'RBRR11': 1,
    'RZTR11': 12
}

# Função para buscar indicadores
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
            "Dividend Yield": round(info.get("dividendYield", 0) * 100, 2) if info.get("dividendYield") else 0,
            "ROE": info.get("returnOnEquity", 0)
        }
    except:
        return {
            "Empresa": ticker,
            "Setor": "-",
            "Preço Atual": 0,
            "P/L": 0,
            "Dividend Yield": 0,
            "ROE": 0
        }

# Tabela de indicadores
st.subheader("📋 Análise dos Indicadores da Carteira")
dados_indicadores = []

for ativo, qtd in carteira.items():
    dados = buscar_indicadores(ativo)
    dados["Ticker"] = ativo
    dados["Quantidade"] = qtd
    dados_indicadores.append(dados)

df_indicadores = pd.DataFrame(dados_indicadores)
st.dataframe(df_indicadores.set_index("Ticker"))

# Simulação de Renda Passiva
st.subheader("💰 Projeção de Metas de Renda Passiva")
metas = [100, 1000, 10000]
capital_total = investimento_inicial
dy_mensal = dy_anual / 100 / 12
renda_mensal = capital_total * dy_mensal
progresso = []
mes = 0

while renda_mensal < metas[-1]:
    renda_mensal = capital_total * dy_mensal
    mes += 1
    capital_total += renda_mensal + aporte_mensal
    for meta in metas:
        if renda_mensal >= meta and meta not in [m['meta'] for m in progresso]:
            progresso.append({"meta": f"R$ {meta}/mês", "meses": mes, "anos": round(mes / 12, 1)})

df_resultado = pd.DataFrame(progresso)
st.table(df_resultado)

# Evolução do capital
st.subheader("📈 Evolução do Capital ao Longo do Tempo")
capital_total = investimento_inicial
capital_mensal = []

for m in range(mes):
    capital_total += capital_total * dy_mensal + aporte_mensal
    capital_mensal.append(capital_total)

st.line_chart(capital_mensal)

st.caption("Simulação baseada em reinvestimento total dos dividendos e aporte constante.")
