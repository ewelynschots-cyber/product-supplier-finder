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
        "facebook": r"^(https?://)?(www\.)?facebook\.com/(?!groups/|events/|pages/|marketplace/|ads/|business/|help/|login/|watch/|gaming/|careers/|policies/|privacy/|terms/|security/|settings/|notifications/|messages/|bookmarks/|saved/|friends/|requests/|fundraisers/|weather/|games/|jobs/|live/|latest/|developers/|platform/|instantarticles/|audience_network/|messenger/|instagram/|whatsapp/|workplace/|oculus/|portal/|sparkar/|horizon/|metaverse/|ai/|research/|news/|blog/|about/|contact/|press/|investor/|partners/|community/|sharer\.php|plugins/)([a-zA-Z0-9\._-]+|profile\.php\?id=\d+)",
        "instagram": r"^(https?://)?(www\.)?instagram\.com/(?!p/|reel/|tv/|explore/|stories/|accounts/|direct/|developer/|about/|legal/)([a-zA-Z0-9\._-]+)",
        "linkedin": r"^(https?://)?(www\.)?linkedin\.com/(in|company)/([a-zA-Z0-9\._-]+)",
    }

    # Domínios de redes sociais a serem ignorados (Twitter, TikTok, WhatsApp, YouTube)
    # Usamos ClassVar para evitar o erro RUF012
    IGNORED_SOCIAL_MEDIA_DOMAINS: ClassVar[list[str]] = [
        "twitter.com",
        "t.co",  # Shortened Twitter links
        "tiktok.com",
        "wa.me",  # WhatsApp direct links
        "youtube.com",
        "youtu.be",  # Shortened YouTube links
    ]

    # Padrão para extrair e-mails
    EMAIL_PATTERN: ClassVar[re.Pattern[str]] = re.compile(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    )

    def extract_all(self, html_content: str, text_content: str) -> Contact:
        """
        Extrai todos os contatos (e-mails e perfis sociais) de um conteúdo HTML e de texto.
        """
        soup = BeautifulSoup(html_content, "html.parser")
        emails = self.extract_emails(text_content)
        social_profiles = self._extract_social_profiles(soup)
        return Contact(emails=emails, social_profiles=social_profiles)

    def extract_emails(self, text_content: str) -> list[str]:
        """Extrai endereços de e-mail de um texto."""
        return list(set(self.EMAIL_PATTERN.findall(text_content)))

    def _extract_social_profiles(self, soup: BeautifulSoup) -> dict[str, str]:
        """Extrai URLs de perfis de redes sociais de um objeto BeautifulSoup."""
        social_profiles = {}
        found_urls = set()

        for link_tag in soup.find_all("a", href=True):
            url = link_tag["href"]
            if url in found_urls:
                continue
            found_urls.add(url)

            # Ignorar domínios indesejados
            if any(domain in url for domain in self.IGNORED_SOCIAL_MEDIA_DOMAINS):
                continue

            for platform, pattern in self.SOCIAL_MEDIA_PATTERNS.items():
                if re.match(pattern, url):
                    social_profiles[platform] = url
                    break  # Encontrou um perfil, passa para o próximo link

        return social_profiles
