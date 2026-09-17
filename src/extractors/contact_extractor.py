"""Extração de e-mails e perfis de redes sociais de conteúdo HTML/texto."""

import re
from typing import ClassVar


class ContactExtractor:
    """Extrai e-mails e links de redes sociais de um texto ou HTML."""

    EMAIL_REGEX = re.compile(
        r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?"
        r"(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)+"
    )

    # Extensões que costumam gerar falsos positivos (ex.: banner@2x.png)
    INVALID_EMAIL_SUFFIXES = (".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp")

    SOCIAL_DOMAINS: ClassVar[dict[str, str]] = {
        "instagram.com": "instagram",
        "facebook.com": "facebook",
        "linkedin.com": "linkedin",
        "twitter.com": "twitter",
        "x.com": "twitter",
        "youtube.com": "youtube",
        "tiktok.com": "tiktok",
        "wa.me": "whatsapp",
    }

    HREF_REGEX = re.compile(r'href=["\'](https?://[^"\']+)["\']', re.IGNORECASE)

    def extract_emails(self, text: str) -> list[str]:
        """Extrai e-mails válidos de um texto, ignorando falsos positivos comuns."""
        found = set(self.EMAIL_REGEX.findall(text))
        valid_emails = {
            email.lower()
            for email in found
            if not email.lower().endswith(self.INVALID_EMAIL_SUFFIXES)
        }
        return sorted(valid_emails)

    def extract_social_profiles(self, html: str) -> dict[str, str]:
        """Extrai links de perfis de redes sociais encontrados em um HTML."""
        profiles: dict[str, str] = {}
        for url in self.HREF_REGEX.findall(html):
            for domain, platform in self.SOCIAL_DOMAINS.items():
                if domain in url and platform not in profiles:
                    profiles[platform] = url
        return profiles

    def extract_all(self, html: str, text: str) -> dict:
        """Extrai e-mails e perfis sociais, retornando ambos em um único dicionário."""
        return {
            "emails": self.extract_emails(text),
            "social_profiles": self.extract_social_profiles(html),
        }
