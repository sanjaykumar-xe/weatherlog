import logging

import httpx

from app import config
from app.errors import AppError

logger = logging.getLogger("weatherlog.provider")

# tests swap this for httpx.MockTransport
transport: httpx.AsyncBaseTransport | None = None


def invalid_response() -> AppError:
    return AppError(502, "provider_invalid_response", "The weather provider returned an unexpected response.")


async def get_json(url: str, params: dict) -> dict:
    try:
        async with httpx.AsyncClient(timeout=config.PROVIDER_TIMEOUT_SECONDS, transport=transport) as client:
            response = await client.get(url, params=params)
    except httpx.TimeoutException:
        logger.warning("Timeout calling %s", url)
        raise AppError(504, "provider_timeout", "The weather provider took too long to respond. Please try again.")
    except httpx.HTTPError as error:
        logger.warning("Request to %s failed: %s", url, type(error).__name__)
        raise AppError(502, "provider_unreachable", "Could not reach the weather provider. Please try again later.")

    if response.status_code == 429:
        logger.warning("Rate limited by %s", url)
        raise AppError(503, "provider_rate_limited", "The weather provider is limiting requests. Please try again shortly.")
    if response.status_code >= 400:
        logger.warning("Provider %s returned %s: %s", url, response.status_code, response.text[:200])
        raise AppError(502, "provider_error", "The weather provider could not complete the request.")

    try:
        data = response.json()
    except ValueError:
        logger.warning("Provider %s returned invalid JSON", url)
        raise invalid_response()
    if not isinstance(data, dict):
        raise invalid_response()
    if data.get("error"):
        logger.warning("Provider %s returned an error payload: %s", url, data.get("reason"))
        raise AppError(502, "provider_error", "The weather provider could not complete the request.")
    return data
