"""Armazenamento dos fornecedores encontrados em arquivo CSV, sem necessidade de banco de dados."""

import csv
import logging
from pathlib import Path

from src.models import Supplier

logger = logging.getLogger(__name__)


class CSVStorage:
    """Salva fornecedores em um arquivo CSV, evitando duplicatas por website."""

    FIELDNAMES = ("name", "website", "emails", "social_profiles")

    def __init__(self, file_path: str = "suppliers.csv"):
        self.file_path = Path(file_path)

    def _load_existing_websites(self) -> set[str]:
        if not self.file_path.exists():
            return set()
        with self.file_path.open("r", newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            return {row["website"] for row in reader}

    def save(self, suppliers: list[Supplier]) -> int:
        """Salva a lista de fornecedores no CSV. Retorna quantos foram efetivamente gravados."""
        existing_websites = self._load_existing_websites()
        file_exists = self.file_path.exists()
        new_count = 0

        with self.file_path.open("a", newline="", encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=self.FIELDNAMES)
            if not file_exists:
                writer.writeheader()

            for supplier in suppliers:
                website_str = str(supplier.website)
                if website_str in existing_websites:
                    continue

                emails = ", ".join(supplier.contact.emails) if supplier.contact else ""
                socials = (
                    ", ".join(
                        f"{platform}: {url}"
                        for platform, url in supplier.contact.social_profiles.items()
                    )
                    if supplier.contact and supplier.contact.social_profiles
                    else ""
                )
                writer.writerow(
                    {
                        "name": supplier.name,
                        "website": website_str,
                        "emails": emails,
                        "social_profiles": socials,
                    }
                )
                new_count += 1

        logger.info("%d novos fornecedores salvos em %s.", new_count, self.file_path)
        return new_count
