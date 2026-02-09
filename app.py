import streamlit as st
import os
import pandas as pd
from parser_proventos import extrair_proventos

st.set_page_config(page_title="Extrator de Dividendos", layout="centered")

st.title("📊 Extrator de Proventos – XP")

# ===============================
# CAMPOS INICIAIS
# ===============================

assessor = st.text_input("Código do Assessor")
conta = st.text_input("Conta do Cliente")

extrato = st.file_uploader("Extrato PDF", type="pdf")
proventos = st.file_uploader("Proventos PDF", type="pdf")

BASE_DIR = "uploads"

# ===============================
# PROCESSAMENTO PDF
# ===============================

if st.button("Processar PDFs"):

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

        st.success("Arquivos salvos 🚀")

        excel_path = f"{pasta_cliente}/relatorio.xlsx"
        sucesso = extrair_proventos(proventos_path, excel_path)

        if sucesso:
            with open(excel_path, "rb") as f:
                st.download_button("Baixar Relatório", f, file_name="relatorio.xlsx")
        else:
            st.error("Não consegui identificar tabelas no PDF")


# ===============================
# UPLOAD CONSENSO (ADMIN)
# ===============================

st.divider()
st.header("🧠 Upload Consenso XP")

consenso_file = st.file_uploader(
    "Enviar consenso atualizado",
    type=["xlsx","xlsm"]
)

if consenso_file:
    with open("consenso_atual.xlsx", "wb") as f:
        f.write(consenso_file.getbuffer())
    st.success("Consenso salvo no sistema")


# ===============================
# UPLOAD POSIÇÃO CLIENTE
# ===============================

st.divider()
st.header("📈 Cruzar Posição x Consenso")

posicao_file = st.file_uploader(
    "Enviar posição consolidada",
    type=["xlsx"]
)

if posicao_file and os.path.exists("consenso_atual.xlsx"):

    posicao = pd.read_excel(posicao_file)
    consenso = pd.read_excel("consenso_atual.xlsx")

    posicao.columns = posicao.columns.str.upper()
    consenso.columns = consenso.columns.str.upper()

    col_pos = [c for c in posicao.columns if "TICK" in c][0]
    col_con = [c for c in consenso.columns if "TICK" in c][0]

    cruzado = posicao.merge(
        consenso,
        left_on=col_pos,
        right_on=col_con,
        how="left"
    )

    st.success("Cruzamento realizado")
    st.dataframe(cruzado)
