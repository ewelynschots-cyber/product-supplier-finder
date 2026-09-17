"""Crawler que visita um site e páginas comuns de contato/sobre para coletar conteúdo."""

import logging
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

from src.http_client import HttpClient

logger = logging.getLogger(__name__)


class SiteCrawler:
    """Visita a página inicial de um site e algumas páginas comuns (contato, sobre)."""

    CANDIDATE_PATHS = (
        "",
        "/contato",
        "/contatos",
        "/contact",
        "/sobre",
        "/sobre-nos",
        "/about",
        "/fale-conosco",
    )

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    def _build_candidate_urls(self, base_url: str) -> list[str]:
        """Monta as URLs candidatas a partir da URL base do site."""
        return [urljoin(base_url, path) for path in self.CANDIDATE_PATHS]

    async def crawl(self, base_url: str) -> tuple[str, str]:
        """
        Visita a página inicial e páginas comuns de contato/sobre de um site.
        Páginas que não existem (404, etc.) são ignoradas silenciosamente,
        sem interromper o crawling das demais.
        Retorna uma tupla (html_concatenado, texto_concatenado).
        """
        combined_html = ""
        combined_text = ""

        for url in self._build_candidate_urls(base_url):
            try:
                response = await self.http_client.get(url)
            except httpx.HTTPStatusError as e:
                logger.debug(
                    "Página %s retornou status %d, ignorando.",
                    url,
                    e.response.status_code,
                )
                continue
            except httpx.RequestError:
                logger.debug("Erro de rede ao acessar %s durante o crawling.", url)
                continue

            if response.status_code == 200:
                combined_html += response.text
                soup = BeautifulSoup(response.text, "lxml")
                combined_text += " " + soup.get_text(separator=" ", strip=True)

        return combined_html, combined_text
