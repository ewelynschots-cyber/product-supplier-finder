"""Agrega múltiplos motores de busca, com fallback automático entre eles."""

import logging

from src.http_client import HttpClient
from src.scrapers.base_search_scraper import BaseSearchScraper
from src.scrapers.brave_search_scraper import BraveSearchScraper
from src.scrapers.startpage_scraper import StartpageScraper
from src.scrapers.web_search_scraper import WebSearchScraper

logger = logging.getLogger(__name__)


class MultiSearchScraper:
    """
    Busca em múltiplos motores (DuckDuckGo, Brave, Startpage), combinando os
    resultados e removendo duplicatas por domínio. Reduz a dependência de um
    único motor, que pode bloquear ou alterar sua estrutura HTML a qualquer momento.
    """

    def __init__(self, http_client: HttpClient):
        self.engines: list[BaseSearchScraper] = [
            WebSearchScraper(http_client),
            BraveSearchScraper(http_client),
            StartpageScraper(http_client),
        ]

    async def search(self, query: str, max_results: int = 5) -> list[dict[str, str]]:
        """Busca em todos os motores configurados e retorna resultados únicos combinados."""
        combined: list[dict[str, str]] = []
        seen_domains: set[str] = set()

        for engine in self.engines:
            if len(combined) >= max_results:
                break
            remaining = max_results - len(combined)
            engine_results = await engine.search(query, max_results=remaining)

            for result in engine_results:
                domain = (
                    result["url"].split("/")[2]
                    if "//" in result["url"]
                    else result["url"]
                )
                if domain in seen_domains:
                    continue
                combined.append(result)
                seen_domains.add(domain)

        logger.info(
            "Total combinado de %d resultados únicos para '%s'.", len(combined), query
        )
        return combined
