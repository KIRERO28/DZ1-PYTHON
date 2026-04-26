import httpx

from app.core.config import settings
from app.core.errors import ExternalServiceError


class OpenRouterClient:
    async def create_chat_completion(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
    ) -> str:
        headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_app_name,
            "Content-Type": "application/json",
        }
        payload = {
            "model": settings.openrouter_model,
            "messages": messages,
            "temperature": temperature,
        }

        try:
            async with httpx.AsyncClient(
                base_url=settings.openrouter_base_url,
                timeout=60.0,
            ) as client:
                response = await client.post("/chat/completions", json=payload, headers=headers)
        except httpx.HTTPError as exc:
            raise ExternalServiceError("Failed to connect to OpenRouter") from exc

        if response.status_code >= 400:
            raise ExternalServiceError(
                f"OpenRouter error {response.status_code}: {response.text}"
            )

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ExternalServiceError("Invalid response format from OpenRouter") from exc
