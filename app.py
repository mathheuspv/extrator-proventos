import streamlit as st
import os
import pandas as pd
from parser_proventos import extrair_proventos

st.set_page_config(page_title="Extrator XP", layout="centered")

ADMIN_PASSWORD = "xp2026"


# ================= HEADER =================

st.title("📊 Extrator de Proventos – XP")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Limpar Tela"):
        st.rerun()

with col2:
    st.link_button("🌐 Baixar Extratos XP", "https://portal.xpi.com.br/")


# ================= LOGIN =================

st.sidebar.title("🔐 Admin")
admin_logado = False
senha = st.sidebar.text_input("Senha admin", type="password")

if senha == ADMIN_PASSWORD:
    admin_logado = True
    st.sidebar.success("Admin autenticado")


# ================= INPUTS =================

assessor = st.text_input("Código do Assessor")
conta = st.text_input("Conta do Cliente")

extrato = st.file_uploader("Extrato PDF", type="pdf")
proventos = st.file_uploader("Proventos PDF", type="pdf")

BASE_DIR = "uploads"


# ================= PROVENTOS =================

if st.button("Processar Proventos"):

    if assessor and conta and extrato and proventos:

        pasta = f"{BASE_DIR}/assessor_{assessor}/cliente_{conta}"
        os.makedirs(pasta, exist_ok=True)

        open(f"{pasta}/extrato.pdf","wb").write(extrato.read())
        open(f"{pasta}/proventos.pdf","wb").write(proventos.read())

        excel_path = f"{pasta}/relatorio.xlsx"

        if extrair_proventos(f"{pasta}/proventos.pdf", excel_path):
            with open(excel_path,"rb") as f:
                st.download_button("⬇️ Baixar Relatório", f)
        else:
            st.error("Falha ao ler PDF")

    else:
        st.error("Preencha tudo")


# ================= CONSENSO ADMIN =================

if admin_logado:

    st.divider()
    st.header("📥 Upload Consenso XP")

    consenso_file = st.file_uploader("Enviar consenso", type=["xlsx","xlsm"])

    if consenso_file:
        with open("consenso_atual.xlsx","wb") as f:
            f.write(consenso_file.getbuffer())

        st.success("Consenso atualizado")


# ================= FUNÇÃO DETECT HEADER XP =================

def ler_posicao_xp(file):

    raw = pd.read_excel(file, header=None)

    linha_header = None

    for i in range(20):
        linha = raw.iloc[i].astype(str).str.upper()

        if any("ATIVO" in x for x in linha):
            linha_header = i
            break

    if linha_header is None:
        st.error("Não achei início da tabela XP")
        st.stop()

    df = pd.read_excel(file, header=linha_header)

    return df


# ================= CRUZAMENTO =================

st.divider()
st.header("📈 Cruzar Posição x Consenso")

posicao_file = st.file_uploader("Enviar posição", type=["xlsx"], key="pos")

if posicao_file:

    posicao = ler_posicao_xp(posicao_file)
    consenso = pd.read_excel("consenso_atual.xlsx")

    st.write("Colunas posição detectadas:")
    st.write(list(posicao.columns))

    # localizar ticker
    ticker_col = None
    for c in posicao.columns:
        if "ATIVO" in str(c).upper():
            ticker_col = c

    if ticker_col is None:
        st.error("Não achei coluna ATIVO")
        st.stop()

    df_pos = posicao[[ticker_col]].copy()
    df_pos.columns = ["Ticker"]

    # consenso (assume padrão)
    df_con = consenso.iloc[:,0:3]
    df_con.columns = ["Ticker","Preco_Alvo","Preco_Atual"]

    cruzado = df_pos.merge(df_con,on="Ticker",how="left")

    cruzado["Upside %"] = (
        (cruzado["Preco_Alvo"] - cruzado["Preco_Atual"])
        / cruzado["Preco_Atual"]
    ) * 100

    st.success("Cruzamento pronto")

    st.dataframe(cruzado)

    cruzado.to_excel("cruzamento.xlsx",index=False)

    with open("cruzamento.xlsx","rb") as f:
        st.download_button("⬇️ Baixar Cruzamento", f)
