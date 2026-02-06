import streamlit as st
import os
from parser_proventos import extrair_proventos

st.set_page_config(page_title="Extrator de Dividendos", layout="centered")

st.title("📊 Extrator de Proventos – XP")

assessor = st.text_input("Código do Assessor")
conta = st.text_input("Conta do Cliente")

extrato = st.file_uploader("Extrato PDF", type="pdf")
proventos = st.file_uploader("Proventos PDF", type="pdf")

BASE_DIR = "uploads"

if st.button("Processar"):

    if not assessor or not conta:
        st.error("Preencha assessor e conta")

    elif not extrato or not proventos:
        st.error("Envie os dois PDFs")

    else:
        # Criar estrutura de pastas
        pasta_cliente = f"{BASE_DIR}/assessor_{assessor}/cliente_{conta}"
        os.makedirs(pasta_cliente, exist_ok=True)

        # Salvar arquivos
        extrato_path = f"{pasta_cliente}/extrato.pdf"
        proventos_path = f"{pasta_cliente}/proventos.pdf"

        with open(extrato_path, "wb") as f:
            f.write(extrato.read())

        with open(proventos_path, "wb") as f:
            f.write(proventos.read())

        st.success("Arquivos salvos com sucesso 🚀")

        # Gerar Excel automaticamente
        excel_path = f"{pasta_cliente}/relatorio.xlsx"

        sucesso = extrair_proventos(proventos_path, excel_path)

        if sucesso:
            st.success("Excel gerado 🎉")

            with open(excel_path, "rb") as f:
                st.download_button(
                    "Baixar Relatório",
                    f,
                    file_name="relatorio.xlsx"
                )
        else:
            st.error("Não consegui identificar tabelas no PDF")

        st.write("Local:")
        st.code(pasta_cliente)

