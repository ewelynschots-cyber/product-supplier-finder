"""Modelos de dados para a plataforma de busca de fornecedores."""

from pydantic import BaseModel, Field, HttpUrl


class ContactInfo(BaseModel):
    """Informações de contato extraídas de um fornecedor."""

    emails: list[str] = Field(
        default_factory=list, description="E-mails encontrados no site do fornecedor."
    )
    social_profiles: dict[str, str] = Field(
        default_factory=dict,
        description="Perfis de redes sociais encontrados, mapeando plataforma -> URL.",
    )


class Supplier(BaseModel):
    """Representa um fornecedor potencial encontrado durante a busca."""

    name: str = Field(..., description="Nome do fornecedor.")
    website: HttpUrl = Field(..., description="URL do site do fornecedor.")
    address: str | None = Field(
        None, description="Endereço físico do fornecedor, se encontrado."
    )
    contact: ContactInfo | None = Field(
        None, description="Informações de contato do fornecedor."
    )
    products_supplied: list[str] = Field(
        default_factory=list, description="Produtos que o fornecedor oferece."
    )


class Product(BaseModel):
    """Representa um produto para o qual buscamos fornecedores."""

    name: str = Field(..., description="Nome do produto.")
    description: str | None = Field(None, description="Descrição detalhada do produto.")
    keywords: list[str] = Field(
        default_factory=list, description="Palavras-chave para a busca."
    )
    potential_suppliers: list[Supplier] = Field(
        default_factory=list, description="Fornecedores potenciais encontrados."
    )
