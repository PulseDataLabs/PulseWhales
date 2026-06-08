from datetime import datetime
from typing import Any

from bs4 import BeautifulSoup

from scrapers.utils.base import BaseScraper
from utils.base import nova_session


def brl_to_float(valor: str) -> float:
    valor = valor.strip().removesuffix("mi").removesuffix("MIl").removesuffix(" Bil").strip()
    if not valor or valor == "-":
        return 0.0
    valor = valor.replace(".", "").replace(",", ".")
    return float(valor)


def parse_br_date(data_str: str) -> str:
    return datetime.strptime(data_str.strip(), "%d/%m/%Y").strftime("%Y-%m-%d")


class B3FluxoEstrangeiroScraper(BaseScraper):
    name = "b3_fluxo_estrangeiro"
    title = "Fluxo Estrangeiro B3 (dadosdemercado.com.br)"
    group = "fluxo"
    phase = 1

    URL = "https://www.dadosdemercado.com.br/fluxo"

    def fetch(self) -> list[dict[str, Any]]:
        session = nova_session()
        response = session.get(self.URL)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table", id="flow")
        if not table:
            raise ValueError("Tabela #flow nao encontrada na pagina.")

        tbody = table.find("tbody")
        if not tbody:
            raise ValueError("Tbody nao encontrado na tabela #flow.")

        linhas: list[dict[str, Any]] = []
        for row in tbody.find_all("tr"):
            cols = row.find_all("td")
            if len(cols) < 6:
                continue

            linhas.append({
                "data": parse_br_date(cols[0].get_text()),
                "estrangeiro": brl_to_float(cols[1].get_text()),
                "institucional": brl_to_float(cols[2].get_text()),
                "pessoa_fisica": brl_to_float(cols[3].get_text()),
                "inst_financeira": brl_to_float(cols[4].get_text()),
                "outros": brl_to_float(cols[5].get_text()),
            })

        linhas.sort(key=lambda x: x["data"])
        return linhas
