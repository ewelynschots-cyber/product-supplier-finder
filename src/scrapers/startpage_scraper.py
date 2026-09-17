"""Scraper para o motor de busca Startpage (versão HTML)."""

from src.scrapers.base_search_scraper import BaseSearchScraper


class StartpageScraper(BaseSearchScraper):
    """Scraper para o motor de busca Startpage."""

    engine_name = "Startpage"
    base_url = "https://www.startpage.com/sp/search"
    excluded_domains = ("startpage.com",)
