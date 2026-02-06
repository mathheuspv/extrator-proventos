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

                # Detecta ticker (linha >>>)
                ticker_match = re.search(r">>>.*?\b([A-Z]{4}\d)\b", linha)
                if ticker_match:
                    ticker_atual = ticker_match.group(1)
                    continue

                # Captura linhas com valores
                if ticker_atual and "R$" in linha and "Pagamento" not in linha:

                    valores = re.findall(r"R\$\s?[\d.,]+", linha)
                    data = re.search(r"\d{2}/\d{2}/\d{4}", linha)

                    if valores and data:

                        # Valor líquido é o último
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
                            "MesNome": dt.strftime("%b/%y"),
                            "Ano": dt.year,
                            "Valor": float(valor)
                        })

    if not registros:
        return False

    df = pd.DataFrame(registros)

    # Ordem cronológica real
    df["Ordem"] = df["Ano"] * 100 + df["MesNum"]

    tabela = df.pivot_table(
        index="Ativo",
        columns="Ordem",
        values="Valor",
        aggfunc="sum",
        fill_value=0
    )

    # Mapear nome bonito das colunas
    mapa = (
        df.drop_duplicates("Ordem")
        .set_index("Ordem")["MesNome"]
        .to_dict()
    )

    tabela.rename(columns=mapa, inplace=True)

    # Ordenar colunas corretamente
    tabela = tabela.reindex(sorted(tabela.columns, key=lambda x: list(mapa.values()).index(x)), axis=1)

    tabela["Total"] = tabela.sum(axis=1)

    tabela.to_excel(output_excel)

    return True
