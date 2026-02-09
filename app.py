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

    if not assessor or not conta:
        st.error("Preencha assessor e conta")

    elif not extrato or not proventos:
        st.error("Envie os dois PDFs")

    else:

        pasta_cliente = f"{BASE_DIR}/assessor_{assessor}/cliente_{conta}"
        os.makedirs(pasta_cliente, exist_ok=True)

        extrato_path = f"{pasta_cliente}/extrato.pdf"
        proventos_path = f"{pasta_cliente}/proventos.pdf"

        with open(extrato_path, "wb") as f:
            f.write(extrato.read())

        with open(proventos_path, "wb") as f:
            f.write(proventos.read())

        excel_path = f"{pasta_cliente}/relatorio.xlsx"
        sucesso = extrair_proventos(proventos_path, excel_path)

        if sucesso:
            with open(excel_path, "rb") as f:
                st.download_button("⬇️ Baixar Relatório", f)
        else:
            st.error("Não consegui identificar tabelas no PDF")


# ================= CONSENSO ADMIN =================

if admin_logado:

    st.divider()
    st.header("📥 Upload Consenso XP")

    consenso_file = st.file_uploader(
        "Enviar planilha consenso",
        type=["xlsx", "xlsm"]
    )

    if consenso_file:
        with open("consenso_atual.xlsx", "wb") as f:
            f.write(consenso_file.getbuffer())

        st.success("Consenso atualizado")


# ================= CRUZAMENTO =================

st.divider()
st.header("📈 Cruzar Posição x Consenso")

posicao_file = st.file_uploader(
    "Enviar posição consolidada",
    type=["xlsx"],
    key="posicao"
)

if posicao_file:

    posicao = pd.read_excel(posicao_file)
    consenso = pd.read_excel("consenso_atual.xlsx")

    # Mostrar colunas para debug
    st.write("Colunas detectadas na posição:")
    st.write(list(posicao.columns))

    # Busca SUPER robusta
    possiveis = [
        "TICK", "ATIVO", "COD", "PROD", "PAPEL",
        "CÓDIGO", "CODIGO", "SYMBOL"
    ]

    col_pos = None
    for p in possiveis:
        for c in posicao.columns:
            if p in str(c).upper():
                col_pos = c
                break
        if col_pos:
            break

    if col_pos is None:
        st.error("Não encontrei ticker — me manda print das colunas")
        st.stop()

    col_con = consenso.columns[0]
    col_alvo = consenso.columns[1]
    col_preco = consenso.columns[2]

    df_pos = posicao[[col_pos]].copy()
    df_pos.columns = ["Ticker"]

    df_con = consenso[[col_con, col_alvo, col_preco]].copy()
    df_con.columns = ["Ticker", "Preco_Alvo", "Preco_Atual"]

    cruzado = df_pos.merge(df_con, on="Ticker", how="left")

    cruzado["Upside %"] = (
        (cruzado["Preco_Alvo"] - cruzado["Preco_Atual"])
        / cruzado["Preco_Atual"]
    ) * 100

    st.dataframe(cruzado)

    cruzado.to_excel("cruzamento.xlsx", index=False)

    with open("cruzamento.xlsx", "rb") as f:
        st.download_button("⬇️ Baixar Cruzamento", f)
