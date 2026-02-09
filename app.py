import streamlit as st
import os
import pandas as pd
from parser_proventos import extrair_proventos

# ===============================
# CONFIG
# ===============================

st.set_page_config(page_title="Extrator XP", layout="centered")

ADMIN_PASSWORD = "xp2026"  # <<< MUDE AQUI SE QUISER


# ===============================
# HEADER
# ===============================

st.title("📊 Extrator de Proventos – XP")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Limpar Tela"):
        st.rerun()

with col2:
    st.link_button(
        "🌐 Baixar Extratos XP",
        "https://portal.xpi.com.br/"
    )

# ===============================
# LOGIN ADMIN
# ===============================

st.sidebar.title("🔐 Admin")

admin_logado = False
senha = st.sidebar.text_input("Senha admin", type="password")

if senha == ADMIN_PASSWORD:
    admin_logado = True
    st.sidebar.success("Admin autenticado")


# ===============================
# INPUTS CLIENTE
# ===============================

assessor = st.text_input("Código do Assessor")
conta = st.text_input("Conta do Cliente")

extrato = st.file_uploader("Extrato PDF", type="pdf")
proventos = st.file_uploader("Proventos PDF", type="pdf")

BASE_DIR = "uploads"


# ===============================
# PROCESSAR PROVENTOS
# ===============================

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

        st.success("Arquivos salvos 🚀")

        excel_path = f"{pasta_cliente}/relatorio.xlsx"
        sucesso = extrair_proventos(proventos_path, excel_path)

        if sucesso:
            st.success("Excel gerado 🎉")

            with open(excel_path, "rb") as f:
                st.download_button(
                    "⬇️ Baixar Relatório",
                    f,
                    file_name="relatorio.xlsx"
                )
        else:
            st.error("Não consegui identificar tabelas no PDF")


# ===============================
# UPLOAD CONSENSO (ADMIN)
# ===============================

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

        st.success("Consenso atualizado ✅")


# ===============================
# CRUZAMENTO POSIÇÃO x CONSENSO
# ===============================

st.divider()
st.header("📈 Cruzar Posição x Consenso")

posicao_file = st.file_uploader(
    "Enviar posição consolidada",
    type=["xlsx"],
    key="posicao"
)

if posicao_file:

    try:
        posicao = pd.read_excel(posicao_file)
        consenso = pd.read_excel("consenso_atual.xlsx")

    except:
        st.error("Consenso ainda não carregado no sistema")
        st.stop()

    # ===== achar colunas automaticamente =====

    def achar_coluna(df, termos):
        for termo in termos:
            for col in df.columns:
                if termo in col.upper():
                    return col
        return None

    col_pos = achar_coluna(posicao, ["TICK", "ATIVO", "COD"])
    col_con = achar_coluna(consenso, ["TICK", "ATIVO", "COD"])
    col_alvo = achar_coluna(consenso, ["ALVO", "TARGET"])
    col_preco = achar_coluna(consenso, ["PRECO", "PRICE"])

    if not col_pos or not col_con:
        st.error("Não consegui identificar colunas de ticker")
        st.stop()

    df_pos = posicao[[col_pos]].copy()
    df_pos.columns = ["Ticker"]

    df_con = consenso[[col_con, col_alvo, col_preco]].copy()
    df_con.columns = ["Ticker", "Preco_Alvo", "Preco_Atual"]

    cruzado = df_pos.merge(df_con, on="Ticker", how="left")

    # ===== calcular upside =====

    if "Preco_Alvo" in cruzado.columns and "Preco_Atual" in cruzado.columns:
        cruzado["Upside %"] = (
            (cruzado["Preco_Alvo"] - cruzado["Preco_Atual"])
            / cruzado["Preco_Atual"]
        ) * 100

    st.success("Cruzamento concluído")

    st.dataframe(cruzado)

    excel_saida = "cruzamento.xlsx"
    cruzado.to_excel(excel_saida, index=False)

    with open(excel_saida, "rb") as f:
        st.download_button(
            "⬇️ Baixar Cruzamento",
            f,
            file_name="cruzamento.xlsx"
        )
