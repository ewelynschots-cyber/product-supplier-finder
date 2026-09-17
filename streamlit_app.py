"""Interface web (Streamlit) para busca de fornecedores de produtos e serviços."""

import asyncio

import streamlit as st

from src.orchestrator import SupplierFinderOrchestrator

ESTADOS_BRASIL = (
    "Todos os estados",
    "Acre",
    "Alagoas",
    "Amapá",
    "Amazonas",
    "Bahia",
    "Ceará",
    "Distrito Federal",
    "Espírito Santo",
    "Goiás",
    "Maranhão",
    "Mato Grosso",
    "Mato Grosso do Sul",
    "Minas Gerais",
    "Pará",
    "Paraíba",
    "Paraná",
    "Pernambuco",
    "Piauí",
    "Rio de Janeiro",
    "Rio Grande do Norte",
    "Rio Grande do Sul",
    "Rondônia",
    "Roraima",
    "Santa Catarina",
    "São Paulo",
    "Sergipe",
    "Tocantins",
)


async def run_search(product: str, state: str | None, max_results: int):
    """Executa a busca de fornecedores de forma assíncrona."""
    orchestrator = SupplierFinderOrchestrator()
    try:
        return await orchestrator.find_suppliers(
            product, state=state, max_results=max_results
        )
    finally:
        await orchestrator.close()


def main() -> None:
    st.set_page_config(page_title="Buscador de Fornecedores", layout="wide")
    st.title("Buscador de Fornecedores")
    st.write(
        "Encontre fornecedores de produtos e serviços, com e-mails e redes sociais "
        "extraídos automaticamente dos sites."
    )

    product = st.text_input(
        "Produto ou serviço", placeholder="ex: parafusos industriais"
    )
    estado_selecionado = st.selectbox("Estado", ESTADOS_BRASIL)
    max_results = st.slider(
        "Número máximo de resultados", min_value=3, max_value=15, value=5
    )

    if st.button("Buscar fornecedores", type="primary"):
        if not product.strip():
            st.warning("Digite um produto ou serviço para buscar.")
            return

        state = None if estado_selecionado == "Todos os estados" else estado_selecionado

        with st.spinner("Buscando fornecedores... isso pode levar alguns minutos."):
            suppliers = asyncio.run(run_search(product, state, max_results))

        if not suppliers:
            st.info("Nenhum fornecedor encontrado. Tente uma busca mais específica.")
            return

        st.success(f"{len(suppliers)} fornecedores encontrados.")

        rows = [
            {
                "Nome": s.name,
                "Site": str(s.website),
                "E-mails": ", ".join(s.contact.emails) if s.contact.emails else "-",
                "Redes sociais": (
                    ", ".join(f"{k}: {v}" for k, v in s.contact.social_profiles.items())
                    if s.contact.social_profiles
                    else "-"
                ),
            }
            for s in suppliers
        ]

        st.dataframe(rows, width="stretch")

        csv_lines = ["Nome,Site,E-mails,Redes sociais"]
        csv_lines.extend(
            f'"{r["Nome"]}","{r["Site"]}","{r["E-mails"]}","{r["Redes sociais"]}"'
            for r in rows
        )
        st.download_button(
            "Baixar resultados em CSV",
            data="\n".join(csv_lines),
            file_name="fornecedores.csv",
            mime="text/csv",
        )


if __name__ == "__main__":
    main()
