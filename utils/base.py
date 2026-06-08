import json
import os
from datetime import datetime, timezone, timedelta
from typing import Any

import pandas as pd
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

HEADERS_HTTP = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7",
}


def agora_brt() -> datetime:
    return datetime.now(timezone(timedelta(hours=-3)))


def criar_diretorio(caminho: str) -> None:
    os.makedirs(caminho, exist_ok=True)


def nova_session(max_retries: int = 3) -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=max_retries,
        backoff_factor=0.5,
        status_forcelist=[500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    session.headers.update(HEADERS_HTTP)
    return session


def salvar_csv(
    dados: list[dict[str, Any]],
    arquivo: str,
    cols: list[str] | None = None,
) -> str:
    df = pd.DataFrame(dados)
    if cols:
        df = df[cols]
    criar_diretorio(os.path.dirname(arquivo) or ".")
    df.to_csv(arquivo, index=False, encoding="utf-8")
    return arquivo


def ler_json(caminho: str) -> Any:
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)
