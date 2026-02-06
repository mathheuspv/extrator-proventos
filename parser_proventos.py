import pdfplumber
import pandas as pd
import re
from datetime import datetime


def extrair_proventos(pdf_path, output_excel):

    registros = []
    ticker_atual = None

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            texto = page.extract_text()

            if not texto:
                continue

            linhas = texto.split("\n")

            for linha in linhas:

                # Detecta ticker
                ticker_match = re.search(r">>>.*?\b([A-Z]{4}\d)\b", linha)
                if ticker_match:
                    ticker_atual = ticker_match.group(1)
                    continue

                # Linhas com valores
                if ticker_atual and "R$" in linha and "Pagamento" not in linha:

                    valores = re.findall(r"R\$\s?[\d.,]+", linha)
                    data = re.search(r"\d{2}/\d{2}/\d{4}", linha)

                    if valores and data:

                        valor = valores[-1]
                        valor = (
                            valor.replace("R$", "")
                            .replace(".", "")
                            .replace(",", ".")
                            .strip()
                        )

                        dt = datetime.strptime(data.group(), "%d/%m/%Y")

                        registros.append({
                            "Ativo": ticker_atual,
                            "MesNum": dt.month,
                            "Ano": dt.year,
                            "MesNome": dt.strftime("%b/%y"),
                            "Valor": float(valor)
                        })

    if not registros:
        return False

    df = pd.DataFrame(registros)

    # Chave cronológica REAL
    df["Ordem"] = df["Ano"] * 100 + df["MesNum"]

    # Pivot
    tabela = df.pivot_table(
        index="Ativo",
        columns="Ordem",
        values="Valor",
        aggfunc="sum",
        fill_value=0
    )
