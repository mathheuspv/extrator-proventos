import streamlit as st
import os
import pandas as pd

from parser_proventos import extrair_proventos

st.set_page_config(page_title="Extrator XP", layout="centered")

# ================================
# HEADER
# ================================

st.title("📊 Extrator de Proventos – XP")

col1, col2 = st.columns(2)

with col1:
    if st.button("🔄 Limpar Tela"):
        st.experimental_rerun()

with col2:
    st.link_button(
        "🌐 Baixar Extratos XP",
        "https://portal.xpi.com.br/"
    )

# ================================
# INPUTS
# ================================

assessor = st.text_input("Código do Assessor")
conta = st.text_input("Conta do Cliente")

extrato = st.file_uploader("Extrato PDF", type="pdf")
proventos = st.file_uploader("Proventos PDF", type="pdf")

BASE_DIR = "uploads"

# ================================
# PROCESSAR PROVENTOS
# ================================

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

        st.code(pasta_cliente)


# ================================
# CONSENSO XP
# ================================

st.header("📥 Upload Consenso XP")

consenso_file = st.file_uploader(
    "Enviar planilha consenso",
    type=["xlsx", "xlsm"],
    key="consenso"
)

if consenso_file:
    with open("consenso_atual.xlsx", "wb") as f:
        f.write(consenso_file.getbuffer())

    st.success("Consenso salvo no sistema")


# ================================
# POSIÇÃO CLIENTE
# ================================

st.header("📈 Cruzar Posição x Consenso")

posicao_file = st.file_uploader(
    "Enviar posição consolidada",
    type=["xlsx"],
    key="posicao"
)

if posicao_file and consenso_file:

    posicao = pd.read_excel(posicao_file)
    consenso = pd.read_excel("consenso_atual.xlsx")

    # ========= achar colunas automaticamente ========

    def achar_coluna(df, termos):
        for t in termos:
            for c in df.columns:
                if t in c.upper():
                    return c
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

    # ========= merge =========

    cruzado = df_pos.merge(df_con, on="Ticker", how="left")

    # ========= calcular upside =========

    if "Preco_Alvo" in cruzado and "Preco_Atual" in cruzado:
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
