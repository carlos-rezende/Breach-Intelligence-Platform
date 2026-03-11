"""Provider de demonstração com dados simulados."""

from app.providers.base_provider import BaseBreachProvider, BreachInfo, BreachResult


class DemoProvider(BaseBreachProvider):
    """Simula vazamentos para fins de demonstração."""

    name = "demo"

    DEMO_EMAILS = {
        "admin@demo.com": [
            BreachInfo("LinkedIn", 2012),
            BreachInfo("Adobe", 2013),
            BreachInfo("Demo Corp", 2020),
        ],
        "test@demo.com": [
            BreachInfo("Gawker", 2010),
            BreachInfo("Stratfor", 2011),
        ],
    }

    def is_available(self) -> bool:
        """Sempre disponível para demonstração."""
        return True

    async def check_email(self, email: str) -> BreachResult:
        """Retorna vazamentos simulados para emails de demo."""
        email_lower = email.lower().strip()
        breaches = self.DEMO_EMAILS.get(email_lower, [])
        return BreachResult(
            provider=self.name,
            breaches=breaches,
            success=True,
        )
