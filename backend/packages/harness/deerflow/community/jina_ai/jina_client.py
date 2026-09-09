import logging
import os

import httpx

logger = logging.getLogger(__name__)

# Default Jina Reader endpoint. Override with JINA_READER_BASE_URL to point
# at a self-hosted Reader-compatible instance (e.g. http://localhost:8080)
# and keep the whole fetch path local — no traffic to r.jina.ai then.
DEFAULT_READER_BASE_URL = "https://r.jina.ai/"

_api_key_warned = False


def get_reader_base_url() -> str:
    base_url = os.getenv("JINA_READER_BASE_URL", "").strip().rstrip("/")
    return base_url or DEFAULT_READER_BASE_URL.rstrip("/")


class JinaClient:
    async def crawl(self, url: str, return_format: str = "html", timeout: int = 10, proxy: str | None = None, trust_env: bool = True) -> str:
        global _api_key_warned
        headers = {
            "Content-Type": "application/json",
            "X-Return-Format": return_format,
            "X-Timeout": str(timeout),
        }
        if os.getenv("JINA_API_KEY"):
            headers["Authorization"] = f"Bearer {os.getenv('JINA_API_KEY')}"
        elif not _api_key_warned:
            _api_key_warned = True
            logger.warning("Jina API key is not set. Provide your own key to access a higher rate limit. See https://jina.ai/reader for more information.")
        data = {"url": url}
        try:
            client_kwargs: dict[str, object] = {"trust_env": trust_env}
            if proxy:
                client_kwargs["proxy"] = proxy
            async with httpx.AsyncClient(**client_kwargs) as client:
                response = await client.post(f"{get_reader_base_url()}/", headers=headers, json=data, timeout=timeout)

            if response.status_code != 200:
                error_message = f"Jina API returned status {response.status_code}: {response.text}"
                logger.error(error_message)
                return f"Error: {error_message}"

            if not response.text or not response.text.strip():
                error_message = "Jina API returned empty response"
                logger.error(error_message)
                return f"Error: {error_message}"

            return response.text
        except Exception as e:
            error_message = f"Request to Jina API failed: {type(e).__name__}: {e}"
            logger.warning(error_message)
            return f"Error: {error_message}"
