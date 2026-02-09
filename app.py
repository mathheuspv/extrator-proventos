import streamlit as st
import os
import pandas as pd
from parser_proventos import extrair_proventos

st.set_page_config(page_title="Extrator XP", layout="wide")

# =====================================================
# LIMPAR TELA
# =====================================================

if st.button("🔄 Limpar Tela"):
    st.session_state.clear()
    st.rerun()

# =====================================================
# FUNÇÃO CONSENSO XP
# =====================================================

def ler_consenso_xp():

    if not os.path.exists("consenso_atual.xlsx"):
        return None

    df = pd.read_excel(
        "consenso_atual.xlsx",
        sheet_name="PDF",
        header=2
    )

    df = df.dropna(how="all")

    # Detectar colunas automaticamente
    col_ticker = [c for c in df.columns if "Ticker" in str(c)][0]
    col_rec = [c for c in df.columns if "#" in str(c) and "Compra" in str(c)][0]
    col_preco = [c for c in df.columns if "Consenso" in str(c)][0]
    col_pot = [c for c in df.columns if "Potencial" in str(c)][0]

    df = df[[col_ticker, col_rec, col_preco, col_pot]]

    df.columns = [
        "Ticker",
        "Recomendacao",
        "Preco_Alvo",
        "Potencial"
    ]

    df["Ticker"] = df["Ticker"].astype(str).str.strip().str.upper()
    df = df.dropna(subset=["Ticker"])

    return df


# =====================================================
# HEADER
# =====================================================

st.title("📊 Extrator de Proventos + Consenso XP")

# =====================================================
# UPLOAD CONSENSO (SÓ VOCÊ)
# =====================================================

with st.expander("🔒 Upload Consenso XP (uso interno)"):
    consenso_file = st.file_uploader(
        "Enviar consenso",
        type=["xlsx","xlsm"],
        key="consenso"
    )

    if consenso_file:
        with open("consenso_atual.xlsx","wb") as f:
            f.write(consenso_file.getbuffer())
        st.success("Consenso atualizado")

# =====================================================
# EXTRATOR PROVENTOS
# =====================================================

st.header("📥 Extrair Proventos")

assessor = st.text_input("Código Assessor")
conta = st.text_input("Conta Cliente")

extrato = st.file_uploader("Extrato PDF", type="pdf")
proventos = st.file_uploader("Proventos PDF", type="pdf")

BASE_DIR = "uploads"

if st.button("Processar PDFs"):

    if not assessor or not conta:
        st.error("Preencha assessor e conta")

    elif not extrato or not proventos:
        st.error("Envie os PDFs")

    else:

        pasta = f"{BASE_DIR}/assessor_{assessor}/cliente_{conta}"
        os.makedirs(pasta, exist_ok=True)

        extrato_path = f"{pasta}/extrato.pdf"
        prov_path = f"{pasta}/proventos.pdf"

        with open(extrato_path,"wb") as f:
            f.write(extrato.read())

        with open(prov_path,"wb") as f:
            f.write(proventos.read())

        excel_path = f"{pasta}/relatorio.xlsx"

        ok = extrair_proventos(prov_path, excel_path)

        if ok:
            st.success("Relatório gerado")

            with open(excel_path,"rb") as f:
                st.download_button(
                    "Baixar Excel",
                    f,
                    file_name="relatorio.xlsx"
                )
        else:
            st.error("Não consegui ler o PDF")

# =====================================================
# CRUZAR POSIÇÃO X CONSENSO
# =====================================================

st.header("📈 Cruzar Posição x Consenso")

pos_file = st.file_uploader(
    "Enviar posição consolidada",
    type=["xlsx"],
    key="pos"
)

if pos_file:

    pos = pd.read_excel(pos_file, header=0)
    pos.columns = pos.columns.astype(str)

    st.write("Colunas detectadas:")
    st.write(list(pos.columns))

    col_ticker = [c for c in pos.columns if "Ativo" in c][0]
    col_qtd = [c for c in pos.columns if "Total" in c or "Qtd" in c][-1]

    pos = pos[[col_ticker, col_qtd]]
    pos.columns = ["Ticker","Quantidade"]

    pos["Ticker"] = pos["Ticker"].astype(str).str.upper()

    consenso = ler_consenso_xp()

    if consenso is None:
        st.warning("Envie o consenso primeiro")

    else:

        final = pos.merge(consenso, on="Ticker", how="left")

        st.success("Cruzamento pronto")
        st.dataframe(final, use_container_width=True)

        excel = final.to_excel("cruzado.xlsx", index=False)

        with open("cruzado.xlsx","rb") as f:
            st.download_button(
                "Baixar Cruzamento",
                f,
                file_name="posicao_consenso.xlsx"
            )
