# src/extractors/contact_extractor.py

import logging
import re
from typing import ClassVar

from bs4 import BeautifulSoup
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class Contact(BaseModel):
    emails: list[str] = Field(default_factory=list)
    social_profiles: dict[str, str] = Field(default_factory=dict)


class ContactExtractor:
    """Extrai informações de contato (e-mails, redes sociais) de uma página HTML."""

    # Padrões de URL para redes sociais válidas (apenas Instagram e LinkedIn)
    # As regex foram simplificadas para serem mais robustas e evitar erros de sintaxe.
    # Elas buscam por padrões de URL de perfil, ignorando links de assets ou páginas genéricas.
    SOCIAL_MEDIA_PATTERNS: ClassVar[dict[str, str]] = {
        "instagram": r"^(https?://)?(www\.)?instagram\.com/([a-zA-Z0-9_.]+)/?$",
        "linkedin": r"^(https?://)?(www\.)?linkedin\.com/(in|company)/([a-zA-Z0-9_-]+)/?$",
    }

    # Domínios de redes sociais a serem ignorados, conforme sua solicitação.
    # Usamos ClassVar para evitar o erro RUF012
    IGNORED_SOCIAL_MEDIA_DOMAINS: ClassVar[list[str]] = [
        "twitter.com", "t.co", "tiktok.com", "wa.me", "youtube.com",
        "facebook.com" # Adicionado facebook.com para ignorar completamente
    ]

    def extract_emails(self, soup: BeautifulSoup) -> list[str]:
        """Extrai endereços de e-mail de uma página HTML."""
        emails = set()
        # Padrão regex para e-mails
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

        # Busca em todo o texto visível
        text = soup.get_text()
        found_emails = re.findall(email_pattern, text)
        for email in found_emails:
            emails.add(email)

        # Busca em links (mailto:)
        for a_tag in soup.find_all("a", href=True):
            if a_tag["href"].startswith("mailto:"):
                email = a_tag["href"][len("mailto:"):]
                emails.add(email)

        return list(emails)

    def _extract_social_profiles(self, soup: BeautifulSoup) -> dict[str, str]:
        """Extrai URLs de perfis de redes sociais de uma página HTML."""
        social_profiles = {}
        found_urls = set()

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]
            # Normaliza a URL para facilitar a comparação
            normalized_href = href.lower().split("?")[0].split("#")[0]

            # Ignora domínios indesejados
            if any(domain in normalized_href for domain in self.IGNORED_SOCIAL_MEDIA_DOMAINS):
                continue

            for platform, pattern in self.SOCIAL_MEDIA_PATTERNS.items():
                if re.match(pattern, normalized_href):
                    if platform not in social_profiles: # Adiciona apenas o primeiro link encontrado por plataforma
                        social_profiles[platform] = href
                        found_urls.add(href)
                    break # Sai do loop de plataformas após encontrar uma correspondência

        return social_profiles

    def extract_all(self, html_content: str, text_content: str = "") -> Contact:
        """
        Extrai todos os contatos (e-mails e perfis sociais) de um conteúdo HTML.
        O parâmetro text_content é opcional e pode ser usado para extrair e-mails
        de texto puro, mas o foco principal é o HTML.
        """
        soup = BeautifulSoup(html_content, "html.parser")

        emails = self.extract_emails(soup)
        social_profiles = self._extract_social_profiles(soup)

        return Contact(emails=emails, social_profiles=social_profiles)
