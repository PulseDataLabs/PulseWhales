# PulseWhales - Fluxo Estrangeiro B3

Acompanhamento diario do fluxo de investidores estrangeiros na B3, com calculo de Z-Score e correlacao com Ibovespa.

## Dados

- **Fluxo estrangeiro**: Scrape de `dadosdemercado.com.br/fluxo` (fonte original: B3). Tabela HTML com dados diarios de Estrangeiro, Institucional, Pessoa Fisica, Inst. Financeira e Outros (em R$ milhoes).
- **Ibovespa**: Yahoo Finance (`^BVSP`) via yfinance.
- **Z-Score**: calculado sobre janela de 90 dias uteis, usando calendario Brazil/ANBIMA com feriados fixos e moveis (Carnaval, Sexta-Feira Santa, Corpus Christi).

## Estrutura

```
PulseWhales/
├── scrapers/
│   ├── b3_fluxo_estrangeiro.py   # Scraper dadosdemercado
│   ├── yahoo_ibov.py             # Scraper Yahoo Finance
│   └── utils/base.py             # BaseScraper (ABC)
├── scripts/
│   ├── processar_fluxo.py        # Merge, Z-Score, gera CSV/JSON
│   └── utils/ux.py               # Logger, banner
├── utils/
│   ├── base.py                   # salvar_csv, nova_session, etc
│   └── calendario.py             # Feriados brasileiros + bizdays Calendar
├── index.html                    # Frontend SPA (Chart.js, dark mode)
├── run_all.py                    # Orquestrador
├── data/                         # CSVs e JSON gerados (git-ignored)
└── .github/workflows/main.yml    # Cron diario via GitHub Actions
```

## Instalacao

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

```bash
# Pipeline completo
python run_all.py

# Apenas um scraper especifico
python run_all.py --scraper b3_fluxo_estrangeiro

# Apenas scrapers, sem processamento
python run_all.py --skip-process

# Filtrar por grupo
python run_all.py --group fluxo
```

Os dados serao salvos em `data/`:
- `b3_fluxo_estrangeiro.csv` - dados brutos do scraper
- `yahoo_ibov.csv` - dados brutos do Ibovespa
- `fluxo_estrangeiro.csv` - dados processados (merjado + Z-Score)
- `fluxo_estrangeiro.json` - dados processados para o frontend

## Frontend

Abra `index.html` no navegador para visualizar o grafico interativo:

- Grafico de barras (fluxo estrangeiro) com eixo dual para Ibovespa
- Cards de resumo: Z-Score, ultimo valor, media 90d, acumulado no ano
- Controles de periodo: 30d, 90d, 180d, 1a, Tudo
- Alternar visibilidade do Ibovespa

## Automacao

O workflow do GitHub Actions executa automaticamente varias vezes ao dia (6h, 8h, 9h, 18h, 21h, 23h BRT) em dias uteis e faz commit dos dados atualizados.

## Licenca

MIT
