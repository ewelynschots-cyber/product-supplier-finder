"""Ponto de entrada da plataforma de busca de fornecedores."""

import asyncio
import logging

from src.orchestrator import SupplierFinderOrchestrator

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def run(product_query: str, max_results: int = 5) -> None:
    orchestrator = SupplierFinderOrchestrator()
    try:
        suppliers = await orchestrator.find_suppliers(
            product_query, max_results=max_results
        )
        if suppliers:
            logger.info(
                "Busca concluída. %d fornecedores salvos em suppliers.csv.",
                len(suppliers),
            )
        else:
            logger.info("Nenhum fornecedor encontrado para '%s'.", product_query)
    finally:
        await orchestrator.close()


if __name__ == "__main__":
    query = input("Digite o produto que deseja buscar fornecedores: ").strip()
    asyncio.run(run(query))
