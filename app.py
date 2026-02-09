import pandas as pd
import streamlit as st


# ========= FUNÇÃO INTELIGENTE =========
def carregar_posicao(uploaded_file):

    # tentativa 1 — leitura normal
    df = pd.read_excel(uploaded_file)

    if any("Ativo" in str(c) for c in df.columns):
        return df

    # tentativa 2 — procurar header manualmente
    raw = pd.read_excel(uploaded_file, header=None)

    for i in range(len(raw)):
        linha = raw.iloc[i].astype(str)

        if linha.str.contains("Ativo", case=False).any():
            df = pd.read_excel(uploaded_file, header=i)
            return df

    raise Exception("Não consegui identificar tabela da posição")


# ========= UPLOAD POSIÇÃO =========
st.header("📈 Cruzar Posição x Consenso")

posicao_file = st.file_uploader(
    "Enviar posição consolidada",
    type=["xlsx"],
    key="posicao"
)

if posicao_file:

    try:
        pos = carregar_posicao(posicao_file)

        st.success("Posição carregada com sucesso ✅")

        # mostrar colunas detectadas
        st.write("Colunas detectadas:")
        st.write(list(pos.columns))

        # preview
        st.dataframe(pos.head())

    except Exception as e:
        st.error(str(e))
