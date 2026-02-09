import streamlit as st
import pandas as pd
import os
from parser_proventos import extrair_proventos

# ================================

# CONFIG

# ================================

st.set_page_config(page_title="Extrator XP", layout="centered")
st.title("📊 Extrator de Proventos – XP")

BASE_DIR = "uploads"
os.makedirs(BASE_DIR, exist_ok=True)

# ================================

# LIMPAR TELA

# ================================

if st.button("🧹 Limpar Tela"):
st.session_state.clear()
st.rerun()

# ================================

# FUNÇÃO — ENCONTRAR HEADER

# ================================

def ler_posicao_auto(file):

```
df_raw = pd.read_excel(file, header=None)

header_row = None

for i, row in df_raw.iterrows():
    if row.astype(str).str.contains("Ativo").any():
        header_row = i
        break

if header_row is None:
    return None

df = pd.read_excel(file, header=header_row)

return df
```

# ================================

# INPUTS PROVENTOS

# ================================

assessor = st.text_input("Código Assessor")
conta = st.text_input("Conta Cliente")

extrato = st.file_uploader("Extrato PDF", type="pdf")
proventos = st.file_uploader("Proventos PDF", type="pdf")

# ================================

# PROCESSAR PROVENTOS

# ================================

if st.button("Processar Proventos"):

```
if assessor and conta and extrato and proventos:

    pasta = f"{BASE_DIR}/assessor_{assessor}/cliente_{conta}"
    os.makedirs(pasta, exist_ok=True)

    extrato_path = f"{pasta}/extrato.pdf"
    prov_path = f"{pasta}/proventos.pdf"
    excel_path = f"{pasta}/relatorio.xlsx"

    with open(extrato_path,"wb") as f:
        f.write(extrato.read())

    with open(prov_path,"wb") as f:
        f.write(proventos.read())

    sucesso = extrair_proventos(prov_path, excel_path)

    if sucesso:
        with open(excel_path,"rb") as f:
            st.download_button("Baixar Relatório", f, file_name="relatorio.xlsx")
    else:
        st.error("Erro lendo PDF")
```

# ================================

# CRUZAR POSIÇÃO

# ================================

st.header("📈 Cruzar Posição x Consenso")

pos_file = st.file_uploader("Posição Cliente", type="xlsx")

if pos_file:

```
pos = ler_posicao_auto(pos_file)

if pos is None:
    st.error("Não achei coluna Ativo")
else:

    st.success("Tabela identificada ✔")

    ticker_col = [c for c in pos.columns if "Ativo" in str(c)][0]
    qtd_col = [c for c in pos.columns if "Posição" in str(c)][0]

    carteira = pos[[ticker_col, qtd_col]].copy()
    carteira.columns = ["Ticker","Quantidade"]

    st.dataframe(carteira)

    st.success("Pronto — base limpa para cruzar consenso 🚀")
```
