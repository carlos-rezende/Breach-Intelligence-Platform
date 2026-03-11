"""Provider Have I Been Pwned."""

from urllib.parse import quote

import httpx

from app.config import get_settings
from app.providers.base_provider import BaseBreachProvider, BreachInfo, BreachResult

settings = get_settings()


class HIBPProvider(BaseBreachProvider):
    """Integração com Have I Been Pwned API."""

    name = "hibp"

    def is_available(self) -> bool:
        """Disponível se API key configurada."""
        return bool(settings.hibp_api_key)

    async def check_email(self, email: str) -> BreachResult:
        """Consulta API HIBP."""
        if not self.is_available():
            return BreachResult(
                provider=self.name,
                breaches=[],
                success=False,
                error="HIBP API key not configured",
            )

        encoded_email = quote(email, safe="")
        url = f"{settings.hibp_base_url}/breachedaccount/{encoded_email}"
        params = {"truncateResponse": "false"}

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    url,
                    params=params,
                    headers={
                        "hibp-api-key": settings.hibp_api_key,
                        "user-agent": settings.hibp_user_agent,
                    },
                )

                if response.status_code == 404:
                    return BreachResult(provider=self.name, breaches=[], success=True)

                if response.status_code != 200:
                    return BreachResult(
                        provider=self.name,
                        breaches=[],
                        success=False,
                        error=f"HIBP API returned {response.status_code}",
                    )

                data = response.json()
                breaches = []
                for item in data:
                    name = item.get("Name", "Unknown")
                    year = None
                    if breach_date := item.get("BreachDate"):
                        try:
                            year = int(breach_date[:4])
                        except (ValueError, TypeError):
                            pass
                    breaches.append(BreachInfo(name=name, year=year, provider=self.name))

                return BreachResult(provider=self.name, breaches=breaches, success=True)

        except Exception as e:
            return BreachResult(
                provider=self.name,
                breaches=[],
                success=False,
                error=str(e),
            )
