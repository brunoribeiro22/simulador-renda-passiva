
import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
from fpdf import FPDF
import base64

st.set_page_config(page_title="Central de Renda Passiva", layout="wide")

st.title("🏦 Central Inteligente de Renda Passiva com Ações da B3")

st.sidebar.header("📥 Importar carteira da corretora")
uploaded_file = st.sidebar.file_uploader("Envie seu arquivo da Ágora (.xlsx)", type=["xlsx"])

def processar_arquivo_agora(file):
    df_all = pd.read_excel(file, sheet_name="Ações FIIs ETFs BDRs")
    df_cleaned = df_all.dropna(how="all").reset_index(drop=True)
    df_final = df_cleaned[5:].reset_index(drop=True)
    df_final.columns = df_final.iloc[0]
    df_final = df_final[1:].reset_index(drop=True)
    df_final = df_final.rename(columns={"Código do ativo": "Ticker", "Quantidade total": "Quantidade", "Preço médio": "PrecoMedio"})
    df_final = df_final[["Ticker", "Quantidade", "PrecoMedio"]]
    df_final.dropna(subset=["Ticker"], inplace=True)
    df_final["Quantidade"] = pd.to_numeric(df_final["Quantidade"], errors="coerce")
    df_final["PrecoMedio"] = pd.to_numeric(df_final["PrecoMedio"], errors="coerce")
    return df_final.dropna()

if uploaded_file:
    carteira_df = processar_arquivo_agora(uploaded_file)
    st.success("Carteira importada com sucesso!")
else:
    carteira_df = pd.DataFrame({
        "Ticker": ["BBAS3", "HAPV3", "JHSF3", "KLBN4", "VALE3", "RBRR11", "RZTR11"],
        "Quantidade": [100, 200, 500, 220, 50, 1, 12],
        "PrecoMedio": [45, 5.8, 3.9, 4.7, 68, 100.0, 10.0]
    })
    st.warning("Usando carteira padrão. Envie um arquivo para atualizar.")

st.sidebar.header("⚙️ Configurações")
aporte_mensal = st.sidebar.number_input("Aporte Mensal (R$)", min_value=0, value=2000, step=100)
investimento_inicial = st.sidebar.number_input("Investimento Inicial (R$)", min_value=0, value=10000, step=100)
dy_anual = st.sidebar.slider("Dividend Yield Anual Estimado (%)", 0.0, 20.0, 8.0, 0.1)
dy_mensal = dy_anual / 100 / 12

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
for index, row in carteira_df.iterrows():
    info = buscar_indicadores(row['Ticker'])
    info["Ticker"] = row['Ticker']
    info["Quantidade"] = row['Quantidade']
    info["Preço Médio"] = row['PrecoMedio']
    if info['Preço Atual']:
        info['YOC (%)'] = round((info['Dividend Yield (%)'] * info['Preço Atual']) / row['PrecoMedio'], 2)
    else:
        info['YOC (%)'] = 0
    dados_analise.append(info)

df_analise = pd.DataFrame(dados_analise)
st.dataframe(df_analise.set_index("Ticker"))

st.subheader("📅 Proximos Dividendos - Datas Com e Pagamento")
dados_dividendos = [
    {"Ticker": "TAEE11", "Data Com": "2025-04-30", "Pagamento": "2025-05-15", "Provento (R$)": 0.74},
    {"Ticker": "BBAS3", "Data Com": "2025-05-10", "Pagamento": "2025-05-20", "Provento (R$)": 0.65},
    {"Ticker": "MXRF11", "Data Com": "2025-05-01", "Pagamento": "2025-05-14", "Provento (R$)": 0.10},
    {"Ticker": "EGIE3", "Data Com": "2025-05-05", "Pagamento": "2025-05-25", "Provento (R$)": 0.55},
    {"Ticker": "ITSA4", "Data Com": "2025-05-07", "Pagamento": "2025-05-22", "Provento (R$)": 0.35},
]
df_dividendos = pd.DataFrame(dados_dividendos)
df_dividendos["DY Estimado (%)"] = df_dividendos["Provento (R$)"] / df_analise.set_index("Ticker")["Preço Atual"] * 100
st.dataframe(df_dividendos)

def gerar_pdf(df, nome="Relatório PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Relatório da Carteira - Meus Dividendos", ln=True, align="C")
    pdf.ln(10)
    for index, row in df.iterrows():
        linha = f"{row['Ticker']}: Quantidade {row['Quantidade']}, Preço Médio {row['Preço Médio']}, YOC {row['YOC (%)']}%, DY {row['Dividend Yield (%)']}%"
        pdf.cell(200, 10, txt=linha, ln=True)
    pdf_file = "/tmp/relatorio_dividendos.pdf"
    pdf.output(pdf_file)
    return pdf_file

if st.button("📄 Gerar PDF da Carteira"):
    pdf_path = gerar_pdf(df_analise)
    with open(pdf_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
        href = f'<a href="data:application/octet-stream;base64,{base64_pdf}" download="relatorio_dividendos.pdf">📥 Clique aqui para baixar o PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

st.subheader("📤 Enviar relatório manualmente por e-mail")
email_input = st.text_input("Digite seu e-mail para receber o relatório:")
if st.button("Enviar por e-mail"):
    if email_input:
        st.info(f"📧 Função de envio será conectada à API de e-mail. Email informado: {email_input}")
    else:
        st.warning("Por favor, preencha um e-mail válido.")
