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

                # Detecta mudança de ativo
                ticker_match = re.search(r">>>.*?\b([A-Z]{4}\d)\b", linha)
                if ticker_match:
                    ticker_atual = ticker_match.group(1)
                    continue

                # Linhas de valores
                if ticker_atual and "R$" in linha and "Pagamento" not in linha:

                    valores = re.findall(r"R\$\s?[\d.,]+", linha)
                    data = re.search(r"\d{2}/\d{2}/\d{4}", linha)

                    if valores and data:

                        valor = valores[-1]
                        valor = valor.replace("R$", "").replace(".", "").replace(",", ".").strip()

                        mes = datetime.strptime(
                            data.group(),
                            "%d/%m/%Y"
                        ).strftime("%b")

                        registros.append({
                            "Ativo": ticker_atual,
                            "Mes": mes,
                            "Valor": float(valor)
                        })

    if not registros:
        return False

    df = pd.DataFrame(registros)

    tabela = df.pivot_table(
        index="Ativo",
        columns="Mes",
        values="Valor",
        aggfunc="sum",
        fill_value=0
    )

    tabela["Total"] = tabela.sum(axis=1)

    tabela.to_excel(output_excel)

    return True
