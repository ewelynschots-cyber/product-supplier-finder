"""Scraper para o motor de busca Brave Search (versão HTML, sem uso de API paga)."""

from src.scrapers.base_search_scraper import BaseSearchScraper


class BraveSearchScraper(BaseSearchScraper):
    """Scraper para o motor de busca Brave Search."""

    engine_name = "Brave Search"
    base_url = "https://search.brave.com/search"
    excluded_domains = ("brave.com",)
