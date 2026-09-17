"""Classe base para scrapers de motores de busca HTML, com extração genérica de links."""

import logging
from urllib.parse import parse_qs, unquote, urlparse

import httpx
from bs4 import BeautifulSoup

from src.http_client import HttpClient

logger = logging.getLogger(__name__)


class BaseSearchScraper:
    """
    Classe base para scrapers de motores de busca que servem resultados em HTML puro.

    Implementa uma extração genérica de links, resiliente a mudanças de classes CSS,
    já que muitos motores de busca alteram sua estrutura HTML com frequência. Subclasses
    só precisam definir `engine_name`, `base_url` e `excluded_domains`.
    """

    engine_name: str = "generic"
    base_url: str = ""
    excluded_domains: tuple[str, ...] = ()

    def __init__(self, http_client: HttpClient):
        self.http_client = http_client

    def _resolve_redirect(self, raw_url: str) -> str | None:
        """Resolve URLs de redirecionamento comuns (ex.: DuckDuckGo /l/?uddg=...)."""
        if raw_url.startswith("/l/?") or "uddg=" in raw_url:
            parsed_qs = parse_qs(urlparse(raw_url).query)
            if parsed_qs.get("uddg"):
                return unquote(parsed_qs["uddg"][0])
            return None
        return raw_url

    def _is_valid_result_url(self, url: str | None) -> bool:
        """Verifica se a URL é válida e não pertence ao próprio motor de busca."""
        if not url or not url.startswith("http"):
            return False
        domain = urlparse(url).netloc.lower()
        return not any(excluded in domain for excluded in self.excluded_domains)

    def _extract_generic_results(
        self, html: str, max_results: int
    ) -> list[dict[str, str]]:
        """
        Extrai resultados de forma genérica: percorre todos os links da página,
        filtra links inválidos/internos do motor de busca e usa o texto do link
        como título. Remove duplicatas por domínio.
        """
        soup = BeautifulSoup(html, "lxml")
        results: list[dict[str, str]] = []
        seen_domains: set[str] = set()

        for a_tag in soup.find_all("a", href=True):
            raw_url = a_tag["href"]
            url = self._resolve_redirect(raw_url)

            if not self._is_valid_result_url(url):
                continue

            domain = urlparse(url).netloc.lower()
            if domain in seen_domains:
                continue

            title = a_tag.get_text(strip=True)
            if not title or len(title) < 3:
                continue

            results.append({"title": title, "url": url})
            seen_domains.add(domain)

            if len(results) >= max_results:
                break

        return results

    async def search(self, query: str, max_results: int = 5) -> list[dict[str, str]]:
        """Realiza a busca no motor configurado e retorna uma lista de {'title', 'url'}."""
        logger.info("[%s] Realizando busca na web para: '%s'", self.engine_name, query)
        try:
            response = await self.http_client.get(self.base_url, params={"q": query})
            results = self._extract_generic_results(response.text, max_results)
            logger.info(
                "[%s] Encontrados %d resultados para a busca '%s'.",
                self.engine_name,
                len(results),
                query,
            )
        except httpx.HTTPStatusError as e:
            logger.error(
                "[%s] Erro HTTP na busca '%s': %s (Status: %d)",
                self.engine_name,
                query,
                e,
                e.response.status_code,
            )
            return []
        except httpx.RequestError as e:
            logger.error(
                "[%s] Erro de requisição na busca '%s': %s", self.engine_name, query, e
            )
            return []
        except Exception:
            logger.exception(
                "[%s] Erro inesperado na busca '%s'", self.engine_name, query
            )
            return []
        else:
            return results
