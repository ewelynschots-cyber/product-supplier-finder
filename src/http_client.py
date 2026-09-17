"""Cliente HTTP assíncrono com retries e backoff exponencial."""

import asyncio
import logging
import random
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class HttpClient:
    """Cliente HTTP reutilizável com retries automáticos e backoff exponencial."""

    MAX_RETRIES = 3
    RETRYABLE_STATUS_CODES = (429, 500, 502, 503, 504)
    INITIAL_DELAY = 1.0
    MAX_DELAY = 10.0

    def __init__(self, timeout: float = 15.0):
        self._client = httpx.AsyncClient(
            timeout=timeout,
            follow_redirects=True,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/124.0.0.0 Safari/537.36"
                )
            },
        )

    async def _request(
        self,
        method: str,
        url: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Executa uma requisição HTTP com retries e backoff exponencial."""
        attempt = 0
        while attempt <= self.MAX_RETRIES:
            try:
                response = await self._client.request(
                    method, url, params=params, data=data, json=json, headers=headers
                )
                response.raise_for_status()
            except httpx.HTTPStatusError as e:
                if (
                    e.response.status_code in self.RETRYABLE_STATUS_CODES
                    and attempt < self.MAX_RETRIES
                ):
                    delay = min(
                        self.MAX_DELAY,
                        self.INITIAL_DELAY * (2**attempt) + random.uniform(0, 1),
                    )
                    logger.warning(
                        "Requisição falhou com status %d para %s. Tentando novamente em %.2f segundos...",
                        e.response.status_code,
                        url,
                        delay,
                    )
                    await asyncio.sleep(delay)
                    attempt += 1
                else:
                    logger.debug(
                        "Requisição para %s retornou status %d (não é um erro de rede).",
                        url,
                        e.response.status_code,
                    )
                    raise
            except httpx.ConnectError as e:
                logger.debug(
                    "Erro de conexão/certificado para %s: %s. Não haverá nova tentativa.",
                    url,
                    e,
                )
                raise
            except httpx.RequestError as e:
                if attempt < self.MAX_RETRIES:
                    delay = min(
                        self.MAX_DELAY,
                        self.INITIAL_DELAY * (2**attempt) + random.uniform(0, 1),
                    )
                    logger.warning(
                        "Erro de requisição para %s. Tentando novamente em %.2f segundos...",
                        url,
                        delay,
                    )
                    await asyncio.sleep(delay)
                    attempt += 1
                else:
                    logger.error("Erro de rede persistente para %s: %s", url, e)
                    raise
            else:
                return response

        raise httpx.RequestError(
            f"Falha na requisição após {self.MAX_RETRIES + 1} tentativas",
            request=httpx.Request(method, url),
        )

    async def get(
        self,
        url: str,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Realiza uma requisição GET."""
        return await self._request("GET", url, params=params, headers=headers)

    async def post(
        self,
        url: str,
        data: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Realiza uma requisição POST."""
        return await self._request("POST", url, data=data, json=json, headers=headers)

    async def close(self) -> None:
        """Fecha a sessão do cliente HTTP."""
        await self._client.aclose()
