"""Provider LeakCheck - API pública gratuita."""

from urllib.parse import quote

import httpx

from app.providers.base_provider import BaseBreachProvider, BreachInfo, BreachResult

LEAKCHECK_PUBLIC_URL = "https://leakcheck.io/api/public"


class LeakCheckProvider(BaseBreachProvider):
    """Integração com LeakCheck API pública (gratuita, sem API key)."""

    name = "leakcheck"

    def is_available(self) -> bool:
        """Sempre disponível - API pública não requer configuração."""
        return True

    async def check_email(self, email: str) -> BreachResult:
        """Consulta API pública LeakCheck."""
        try:
            encoded = quote(email, safe="")
            url = f"{LEAKCHECK_PUBLIC_URL}?check={encoded}"

            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url)

                if response.status_code != 200:
                    return BreachResult(
                        provider=self.name,
                        breaches=[],
                        success=False,
                        error=f"LeakCheck API returned {response.status_code}",
                    )

                data = response.json()
                if not data.get("success") or not data.get("sources"):
                    return BreachResult(provider=self.name, breaches=[], success=True)

                breaches = []
                for src in data["sources"]:
                    name = src.get("name", "Unknown")
                    year = None
                    if date_str := src.get("date"):
                        try:
                            year = int(str(date_str)[:4])
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
