"""Scraper para o motor de busca DuckDuckGo (versão HTML)."""

from src.scrapers.base_search_scraper import BaseSearchScraper


class WebSearchScraper(BaseSearchScraper):
    """Scraper para o motor de busca DuckDuckGo."""

    engine_name = "DuckDuckGo"
    base_url = "https://html.duckduckgo.com/html/"
    excluded_domains = ("duckduckgo.com",)
