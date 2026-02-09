import pdfplumber
import pandas as pd
import re
from datetime import datetime


# ==========================================================
# FUNÇÃO PRINCIPAL
# ==========================================================
def extrair_proventos(pdf_path, output_excel):

    registros = []
    ticker_atual = None

    print("🔎 Lendo PDF...")

    with pdfplumber.open(pdf_path) as pdf:

        for page in pdf.pages:

            texto = page.extract_text()

            if not texto:
                continue

            linhas = texto.split("\n")

            for linha in linhas:

                # ==================================================
                # DETECTAR TICKER (ROBUSTO)
                # ==================================================
                ticker_match = re.search(r"\b[A-Z]{4}\d{1,2}\b", linha)

                if ticker_match:
                    ticker_atual = ticker_match.group()

                # ==================================================
                # DETECTAR DATA + VALOR
                # ==================================================
                if ticker_atual:

                    data_match = re.search(r"\d{2}/\d{2}/\d{4}", linha)
                    valores = re.findall(r"R\$\s?[\d.,]+", linha)

                    if data_match and valores:

                        try:
                            valor = valores[-1]

                            valor = (
                                valor.replace("R$", "")
                                .replace(".", "")
                                .replace(",", ".")
                                .strip()
                            )

                            dt = datetime.strptime(
                                data_match.group(),
                                "%d/%m/%Y"
                            )

                            registros.append({
                                "Ativo": ticker_atual,
                                "MesNum": dt.month,
                                "Ano": dt.year,
                                "MesNome": dt.strftime("%b/%y"),
                                "Valor": float(valor)
                            })

                        except Exception as e:
                            print("Erro parse:", e)
                            pass


    # ==========================================================
    # SE NÃO ENCONTROU NADA
    # ==========================================================
    if not registros:
        print("❌ Nenhum provento encontrado")
        return False


    # ==========================================================
    # TABELA FINAL
    # ==========================================================
    df = pd.DataFrame(registros)

    df["Ordem"] = df["Ano"] * 100 + df["MesNum"]

    tabela = df.pivot_table(
        index="Ativo",
        columns="Ordem",
        values="Valor",
        aggfunc="sum",
        fill_value=0
    )

    tabela = tabela.reindex(sorted(tabela.columns), axis=1)

    mapa = (
        df.drop_duplicates("Ordem")
        .set_index("Ordem")["MesNome"]
        .to_dict()
    )

    tabela.rename(columns=mapa, inplace=True)

    tabela["Total"] = tabela.sum(axis=1)

    # ==========================================================
    # EXPORTAR
    # ==========================================================
    tabela.to_excel(output_excel)

    print("✅ Extração concluída")
    print("Linhas encontradas:", len(tabela))

    return True
