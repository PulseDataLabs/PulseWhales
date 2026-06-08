import json
import os
from datetime import date, datetime

import bizdays
import pandas as pd

from scripts.utils.ux import LOG
from utils.base import criar_diretorio
from utils.calendario import feriados_br

DATA_DIR = "data"
SCRAPER_CSV = os.path.join(DATA_DIR, "b3_fluxo_estrangeiro.csv")
ACUMULADO_CSV = os.path.join(DATA_DIR, "fluxo_estrangeiro.csv")
IBOV_CSV = os.path.join(DATA_DIR, "yahoo_ibov.csv")
OUTPUT_JSON = os.path.join(DATA_DIR, "fluxo_estrangeiro.json")
ZSCORE_WINDOW = 90


def _calcular_zscore(s: pd.Series) -> float:
    if s.std() == 0:
        return 0.0
    return (s.iloc[-1] - s.mean()) / s.std()


def _acumular_dados() -> pd.DataFrame:
    if not os.path.exists(SCRAPER_CSV):
        if os.path.exists(ACUMULADO_CSV):
            LOG.info("Carregando dados acumulados existentes...")
            return pd.read_csv(ACUMULADO_CSV)
        LOG.error(f"Arquivo nao encontrado: {SCRAPER_CSV}")
        return pd.DataFrame()

    LOG.info("Carregando dados do scraper...")
    novo = pd.read_csv(SCRAPER_CSV)
    novo["data"] = pd.to_datetime(novo["data"]).dt.date

    if os.path.exists(ACUMULADO_CSV):
        LOG.info("Carregando dados acumulados existentes...")
        antigo = pd.read_csv(ACUMULADO_CSV)
        antigo["data"] = pd.to_datetime(antigo["data"]).dt.date
        combinado = pd.concat([antigo, novo], ignore_index=True)
    else:
        combinado = novo

    combinado = combinado.drop_duplicates(subset=["data"]).sort_values("data").reset_index(drop=True)
    return combinado


def processar() -> None:
    criar_diretorio(DATA_DIR)

    fluxo = _acumular_dados()
    if fluxo.empty:
        return

    LOG.info(f"Dados acumulados: {len(fluxo)} registros ({fluxo['data'].min()} a {fluxo['data'].max()})")

    if os.path.exists(IBOV_CSV):
        LOG.info("Carregando dados do Ibovespa...")
        ibov = pd.read_csv(IBOV_CSV)
        ibov["data"] = pd.to_datetime(ibov["data"]).dt.date
        fluxo = fluxo.merge(ibov, on="data", how="left")

    anos = set(fluxo["data"].apply(lambda d: d.year))
    holidays = list({h for ano in anos for h in feriados_br(ano)})
    cal = bizdays.Calendar(holidays=holidays, weekdays=["Saturday", "Sunday"])

    fluxo["_data_dt"] = pd.to_datetime(fluxo["data"])
    fluxo = fluxo[fluxo["_data_dt"].apply(lambda d: cal.isbizday(d))].copy()

    LOG.info(f"Calculando Z-Score (janela de {ZSCORE_WINDOW} dias uteis)...")
    fluxo["z_score_estrangeiro"] = (
        fluxo["estrangeiro"]
        .rolling(window=ZSCORE_WINDOW, min_periods=ZSCORE_WINDOW)
        .apply(_calcular_zscore, raw=False)
    )

    fluxo = fluxo.drop(columns=["_data_dt"]).round(2)

    fluxo["data"] = fluxo["data"].astype(str)

    fluxo.to_csv(ACUMULADO_CSV, index=False, encoding="utf-8")
    LOG.info(f"CSV salvo: {ACUMULADO_CSV} ({len(fluxo)} registros)")

    hoje = date.today()
    ano_atual = hoje.year
    fluxo_ano = fluxo[pd.to_datetime(fluxo["data"]).dt.year == ano_atual]

    ultimo = fluxo.iloc[-1]
    ultimos_90 = fluxo.tail(ZSCORE_WINDOW)

    resumo = {
        "z_score_atual": (
            round(float(ultimo["z_score_estrangeiro"]), 2)
            if pd.notna(ultimo.get("z_score_estrangeiro"))
            else None
        ),
        "media_90d": round(float(ultimos_90["estrangeiro"].mean()), 2),
        "desvio_90d": round(float(ultimos_90["estrangeiro"].std()), 2),
        "acumulado_ano": round(float(fluxo_ano["estrangeiro"].sum()), 2),
        "ultimo_valor": round(float(ultimo["estrangeiro"]), 2),
        "ultima_data": str(ultimo["data"]),
    }

    jsn = {
        "ultima_atualizacao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "dias": fluxo.to_dict(orient="records"),
        "resumo": resumo,
    }

    for d in jsn["dias"]:
        for k, v in d.items():
            if isinstance(v, float) and (v != v):
                d[k] = None

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(jsn, f, ensure_ascii=False, indent=2)

    LOG.info(f"JSON salvo: {OUTPUT_JSON}")
    LOG.info(f"Z-Score atual: {resumo['z_score_atual']}")
    LOG.info(f"Ultimo valor: {resumo['ultimo_valor']}")


if __name__ == "__main__":
    processar()
