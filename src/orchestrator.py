"""Orquestrador principal: busca na web, crawling e extração de contatos de fornecedores."""

import asyncio
import logging

from src.extractors.contact_extractor import ContactExtractor
from src.filters.relevance_filter import RelevanceFilter
from src.http_client import HttpClient
from src.models import ContactInfo, Supplier
from src.scrapers.multi_search_scraper import MultiSearchScraper
from src.scrapers.site_crawler import SiteCrawler
from src.storage.csv_storage import CSVStorage

logger = logging.getLogger(__name__)


class SupplierFinderOrchestrator:
    """Coordena busca (múltiplos motores), filtro de relevância, crawling e extração de contatos."""

    def __init__(self):
        self.http_client = HttpClient()
        self.search_scraper = MultiSearchScraper(self.http_client)
        self.site_crawler = SiteCrawler(self.http_client)
        self.contact_extractor = ContactExtractor()
        self.storage = CSVStorage()
        self.relevance_filter = RelevanceFilter()

    async def find_suppliers(
        self,
        product_query: str,
        state: str | None = None,
        max_results: int = 5,
    ) -> list[Supplier]:
        """Busca fornecedores para um produto (opcionalmente filtrado por estado)."""
        full_query = f"{product_query} em {state}" if state else product_query
        logger.info("Iniciando busca de fornecedores para: '%s'", full_query)

        raw_results = await self.search_scraper.search(
            full_query, max_results=max_results * 2
        )
        filtered_results = self.relevance_filter.filter_results(raw_results)
        search_results = filtered_results[:max_results]

        logger.info(
            "Resultados brutos: %d | Após filtro de relevância: %d | Usados: %d",
            len(raw_results),
            len(filtered_results),
            len(search_results),
        )

        suppliers: list[Supplier] = []
        for result in search_results:
            website = result["url"]
            title = result["title"]

            html, text = await self.site_crawler.crawl(website)
            if not html:
                logger.warning("Nenhum conteúdo coletado para %s, pulando.", website)
                continue

            extracted = self.contact_extractor.extract_all(html, text)
            contact = ContactInfo(
                emails=extracted["emails"],
                social_profiles=extracted["social_profiles"],
            )

            try:
                supplier = Supplier(name=title, website=website, contact=contact)
            except ValueError:
                logger.warning(
                    "URL inválida para o fornecedor '%s': %s", title, website
                )
                continue

            suppliers.append(supplier)
            logger.info(
                "Fornecedor processado: %s | E-mails: %s | Redes sociais: %s",
                supplier.name,
                contact.emails,
                list(contact.social_profiles.keys()),
            )

        if suppliers:
            self.storage.save(suppliers)

        return suppliers

    async def close(self) -> None:
        """Fecha o cliente HTTP."""
        await self.http_client.close()


async def _demo() -> None:
    logging.basicConfig(level=logging.INFO)
    orchestrator = SupplierFinderOrchestrator()
    try:
        suppliers = await orchestrator.find_suppliers(
            "fornecedores de parafusos industriais", state="São Paulo", max_results=5
        )
        logger.info("Total de fornecedores encontrados: %d", len(suppliers))
    finally:
        await orchestrator.close()


if __name__ == "__main__":
    asyncio.run(_demo())
