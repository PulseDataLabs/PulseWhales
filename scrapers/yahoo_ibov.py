from typing import Any

import yfinance as yf

from scrapers.utils.base import BaseScraper


class YahooIbovScraper(BaseScraper):
    name = "yahoo_ibov"
    title = "Ibovespa (Yahoo Finance)"
    group = "fluxo"
    phase = 2

    TICKER = "^BVSP"

    def fetch(self) -> list[dict[str, Any]]:
        ticker = yf.Ticker(self.TICKER)
        df = ticker.history(period="max")
        dados: list[dict[str, Any]] = []
        for idx, row in df.iterrows():
            dados.append({
                "data": idx.strftime("%Y-%m-%d"),
                "ibov_fechamento": round(float(row["Close"]), 2),
            })
        return dados
