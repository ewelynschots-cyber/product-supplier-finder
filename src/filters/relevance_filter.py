"""Filtro de relevância: descarta resultados que claramente não são fornecedores/empresas."""

from typing import ClassVar


class RelevanceFilter:
    """
    Remove da lista de resultados páginas que não representam empresas/fornecedores,
    como enciclopédias, dicionários, portais de notícias e sites puramente informativos.
    """

    EXCLUDED_DOMAINS: ClassVar[tuple[str, ...]] = (
        "wikipedia.org",
        "wikihow.com",
        "dicio.com.br",
        "significados.com.br",
        "todamateria.com.br",
        "brasilescola.uol.com.br",
        "infoescola.com",
        "google.com",
        "youtube.com",
        "reclameaqui.com.br",
        "horariodebrasilia.org",
        "tempo.com",
        "climatempo.com.br",
        "gov.br",
    )

    EXCLUDED_TITLE_KEYWORDS: ClassVar[tuple[str, ...]] = (
        "wikipédia",
        "wikipedia",
        "o que é",
        "significado",
        "hora certa",
        "horário",
        "dicionário",
        "definição",
    )

    def is_relevant(self, title: str, url: str) -> bool:
        """Retorna False se o resultado parecer claramente não comercial."""
        url_lower = url.lower()
        title_lower = title.lower()

        if any(domain in url_lower for domain in self.EXCLUDED_DOMAINS):
            return False

        return not any(
            keyword in title_lower for keyword in self.EXCLUDED_TITLE_KEYWORDS
        )

    def filter_results(self, results: list[dict[str, str]]) -> list[dict[str, str]]:
        """Filtra uma lista de resultados de busca, mantendo apenas os relevantes."""
        return [r for r in results if self.is_relevant(r["title"], r["url"])]
