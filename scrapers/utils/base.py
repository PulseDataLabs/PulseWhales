from abc import ABC, abstractmethod
from typing import Any

from utils.base import salvar_csv


class BaseScraper(ABC):
    name: str = ""
    title: str = ""
    group: str = "default"
    phase: int = 1

    def __init__(self) -> None:
        if not self.name:
            self.name = self.__class__.__name__.lower()

    @abstractmethod
    def fetch(self) -> list[dict[str, Any]]:
        ...

    def run(self, arquivo: str | None = None) -> list[dict[str, Any]]:
        dados = self.fetch()
        if arquivo and dados:
            cols = list(dados[0].keys())
            salvar_csv(dados, arquivo, cols)
        return dados
