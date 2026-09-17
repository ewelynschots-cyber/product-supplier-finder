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

    # Padrões de URL para redes sociais válidas (apenas Facebook, Instagram, LinkedIn)
    # Usamos ClassVar para evitar o erro RUF012
    SOCIAL_MEDIA_PATTERNS: ClassVar[dict[str, str]] = {
        "facebook": r"^(https?://)?(www\.)?facebook\.com/([a-zA-Z0-9\._-]+/?)$",
        "instagram": r"^(https?://)?(www\.)?instagram\.com/([a-zA-Z0-9\._-]+/?)$",
        "linkedin": r"^(https?://)?(www\.)?linkedin\.com/(in|company)/([a-zA-Z0-9\._-]+/?)$",
    }

    # Domínios de redes sociais que queremos ignorar completamente
    IGNORED_SOCIAL_MEDIA_DOMAINS: ClassVar[list[str]] = [
        "twitter.com",
        "t.co",  # Redirecionador comum do Twitter
        "tiktok.com",
        "wa.me",  # WhatsApp
        "youtube.com",  # Adicionado para ignorar YouTube
        "olx.com.br",  # Adicionado para ignorar OLX
        "static.olx.com.br",  # Adicionado para ignorar assets da OLX
    ]

    def extract_emails(self, soup: BeautifulSoup) -> list[str]:
        """Extrai endereços de e-mail de um objeto BeautifulSoup."""
        emails = set()
        # Expressão regular para encontrar e-mails
        email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
        text = soup.get_text()
        found_emails = re.findall(email_pattern, text)
        for email in found_emails:
            # Filtra e-mails que são provavelmente de assets ou links inválidos
            if not any(
                ext in email.lower() for ext in [".png", ".jpg", ".gif", ".css", ".js"]
            ):
                emails.add(email)
        return list(emails)

    def _extract_social_profiles(self, soup: BeautifulSoup) -> dict[str, str]:
        """Extrai URLs de perfis de redes sociais de um objeto BeautifulSoup."""
        social_profiles = {}
        for link in soup.find_all("a", href=True):
            url = link["href"]
            # Ignorar domínios indesejados
            if any(domain in url for domain in self.IGNORED_SOCIAL_MEDIA_DOMAINS):
                continue

            for platform, pattern in self.SOCIAL_MEDIA_PATTERNS.items():
                if re.match(pattern, url):
                    # Adiciona apenas o primeiro perfil encontrado para cada plataforma
                    if platform not in social_profiles:
                        social_profiles[platform] = url
                        logger.debug(f"Found social profile: {platform}: {url}")
                    break  # Sai do loop de plataformas para evitar duplicação
        return social_profiles

    def extract_contacts(self, soup: BeautifulSoup) -> Contact:
        """Extrai todos os contatos (e-mails e redes sociais) de um objeto BeautifulSoup."""
        emails = self.extract_emails(soup)
        social_profiles = self._extract_social_profiles(soup)
        return Contact(emails=emails, social_profiles=social_profiles)
