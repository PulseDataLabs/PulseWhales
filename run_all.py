import argparse
import importlib
import os
import sys

import scrapers
from scrapers.utils.base import BaseScraper
from scripts.processar_fluxo import processar
from scripts.utils.ux import LOG, banner


def descobrir_scrapers() -> list[BaseScraper]:
    encontrados: list[BaseScraper] = []
    scraper_dir = os.path.dirname(scrapers.__file__)
    for entry in os.scandir(scraper_dir):
        if entry.name.startswith("_") or entry.name.startswith("."):
            continue
        if entry.is_file() and entry.name.endswith(".py"):
            module_name = f"scrapers.{entry.name[:-3]}"
            try:
                mod = importlib.import_module(module_name)
                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if (
                        isinstance(attr, type)
                        and issubclass(attr, BaseScraper)
                        and attr is not BaseScraper
                    ):
                        encontrados.append(attr())
            except Exception as e:
                LOG.error(f"Erro ao carregar {module_name}: {e}")
    return encontrados


def main() -> None:
    parser = argparse.ArgumentParser(description="PulseWhales - Fluxo Estrangeiro B3")
    banner()
    parser.add_argument("--group", type=str, help="Executar apenas scrapers de um grupo")
    parser.add_argument("--scraper", type=str, help="Executar apenas um scraper especifico")
    parser.add_argument("--skip-process", action="store_true", help="Pular processamento")
    args = parser.parse_args()

    scrapers_encontrados = descobrir_scrapers()
    scrapers_encontrados.sort(key=lambda s: s.phase)

    LOG.info(f"Scrapers encontrados: {len(scrapers_encontrados)}")

    for scraper in scrapers_encontrados:
        if args.group and scraper.group != args.group:
            continue
        if args.scraper and scraper.name != args.scraper:
            continue

        arquivo = f"data/{scraper.name}.csv"
        LOG.info(f"Executando: {scraper.title} (fase {scraper.phase})")
        try:
            dados = scraper.run(arquivo=arquivo)
            LOG.info(f"  -> {len(dados)} registros obtidos")
        except Exception as e:
            LOG.error(f"  -> Erro: {e}")

    if not args.skip_process:
        LOG.info("Executando processamento dos dados...")
        processar()

    LOG.info("Concluido!")


if __name__ == "__main__":
    main()
