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

# FUNÇÃO — ENCONTRAR HEADER REAL

# =====================================================

def ler_posicao_xp(file):

```
raw = pd.read_excel(file, header=None)

header_row = None

for i in range(len(raw)):
    linha = raw.iloc[i].astype(str)
    if linha.str.contains("Ativo").any():
        header_row = i
        break

if header_row is None:
    st.error("Não achei linha do header (Ativo)")
    return None

df = pd.read_excel(file, header=header_row)

df.columns = df.columns.astype(str)

col_ticker = [c for c in df.columns if "Ativo" in c][0]
col_qtd = [c for c in df.columns if "Total" in c][-1]

df = df[[col_ticker, col_qtd]]
df.columns = ["Ticker","Quantidade"]

df["Ticker"] = df["Ticker"].astype(str).str.upper()

return df
```

# =====================================================

# CONSENSO XP

# =====================================================

def ler_consenso_xp():

```
if not os.path.exists("consenso_atual.xlsx"):
    return None

raw = pd.read_excel("consenso_atual.xlsx", sheet_name="PDF", header=None)

header_row = None

for i in range(len(raw)):
    linha = raw.iloc[i].astype(str)

    if linha.str.contains("Ticker").any():
        header_row = i
        break

df = pd.read_excel(
    "consenso_atual.xlsx",
    sheet_name="PDF",
    header=header_row
)

df = df.dropna(how="all")

col_ticker = [c for c in df.columns if "Ticker" in str(c)][0]
col_rec = [c for c in df.columns if "Compra" in str(c)][0]
col_preco = [c for c in df.columns if "Consenso" in str(c)][0]
col_pot = [c for c in df.columns if "Potencial" in str(c)][0]

df = df[[col_ticker, col_rec, col_preco, col_pot]]

df.columns = ["Ticker","Recomendacao","Preco_Alvo","Potencial"]

df["Ticker"] = df["Ticker"].astype(str).str.strip().str.upper()

return df
```

# =====================================================

# UI

# =====================================================

st.title("📊 Extrator XP — Proventos + Consenso")

# Upload Consenso (interno)

with st.expander("🔒 Upload Consenso XP"):
consenso_file = st.file_uploader("Enviar consenso", type=["xlsx","xlsm"])

```
if consenso_file:
    with open("consenso_atual.xlsx","wb") as f:
        f.write(consenso_file.getbuffer())
    st.success("Consenso atualizado")
```

# =====================================================

# PROVENTOS

# =====================================================

st.header("📥 Extrair Proventos")

assessor = st.text_input("Assessor")
conta = st.text_input("Conta")

extrato = st.file_uploader("Extrato PDF", type="pdf")
proventos = st.file_uploader("Proventos PDF", type="pdf")

if st.button("Processar PDFs"):

```
pasta = f"uploads/{assessor}_{conta}"
os.makedirs(pasta, exist_ok=True)

extrato_path = f"{pasta}/extrato.pdf"
prov_path = f"{pasta}/prov.pdf"

with open(extrato_path,"wb") as f:
    f.write(extrato.read())

with open(prov_path,"wb") as f:
    f.write(proventos.read())

excel_path = f"{pasta}/relatorio.xlsx"

ok = extrair_proventos(prov_path, excel_path)

if ok:
    with open(excel_path,"rb") as f:
        st.download_button("Baixar Excel", f, file_name="relatorio.xlsx")
```

# =====================================================

# CRUZAMENTO

# =====================================================

st.header("📈 Cruzar Posição x Consenso")

pos_file = st.file_uploader("Enviar posição XP", type="xlsx")

if pos_file:

```
pos = ler_posicao_xp(pos_file)

if pos is not None:

    consenso = ler_consenso_xp()

    if consenso is None:
        st.warning("Envie o consenso primeiro")

    else:

        final = pos.merge(consenso, on="Ticker", how="left")

        st.dataframe(final, use_container_width=True)

        final.to_excel("cruzado.xlsx", index=False)

        with open("cruzado.xlsx","rb") as f:
            st.download_button("Baixar Cruzamento", f)
```
