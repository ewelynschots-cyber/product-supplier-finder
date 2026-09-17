# src/orchestrator.py

import logging

from src.extractors.contact_extractor import Contact, ContactExtractor
from src.extractors.info_extractor import InfoExtractor
from src.models import Supplier  # Assuming Supplier is defined here or imported
from src.scrapers.google_scraper import GoogleScraper
from src.scrapers.olx_scraper import OLXScraper

logger = logging.getLogger(__name__)


class Orchestrator:
    def __init__(self):
        self.google_scraper = GoogleScraper()
        self.olx_scraper = OLXScraper()
        self.info_extractor = InfoExtractor()
        self.contact_extractor = ContactExtractor()

    async def find_suppliers(
        self, product: str, state: str, max_results: int
    ) -> list[Supplier]:
        search_query = f"{product} {state}"
        logger.info(f"Iniciando busca por: {search_query}")

        # Busca no Google
        google_results = await self.google_scraper.search(search_query, max_results)
        logger.info(f"Encontrados {len(google_results)} resultados no Google.")

        suppliers: list[Supplier] = []
        for result in google_results:
            # Extrair informações da página do fornecedor
            page_content = await self.info_extractor.fetch_page_content(result.link)
            if page_content:
                html_content, text_content = page_content

                # Extrair contatos usando o ContactExtractor
                # Acessar atributos do objeto Contact com notação de ponto
                extracted_contacts: Contact = self.contact_extractor.extract_all(
                    html_content, text_content
                )

                supplier = Supplier(
                    name=result.title,
                    site=result.link,
                    emails=extracted_contacts.emails,  # Correção aqui
                    social_profiles=extracted_contacts.social_profiles,  # Correção aqui
                    phone_numbers=[],  # Adicionei um placeholder, se não for extraído
                    whatsapp_numbers=[],  # Adicionei um placeholder, se não for extraído
                )
                suppliers.append(supplier)
            else:
                logger.warning(
                    f"Não foi possível extrair conteúdo da página: {result.link}"
                )

        # Busca na OLX (se necessário e implementado)
        # olx_results = await self.olx_scraper.search(search_query, max_results)
        # for result in olx_results:
        #     # Processar resultados da OLX de forma similar
        #     pass

        return suppliers
