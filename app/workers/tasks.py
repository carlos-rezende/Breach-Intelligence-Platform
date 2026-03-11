"""Tarefas Celery para processamento assíncrono."""

from app.workers.celery_app import celery_app


@celery_app.task(bind=True)
def check_breach_async(self, email: str):
    """
    Tarefa assíncrona para verificação de vazamento.
    Útil quando múltiplos providers são consultados.
    """
    from app.providers.demo_provider import DemoProvider
    from app.providers.hibp_provider import HIBPProvider

    providers = [DemoProvider(), HIBPProvider()]
    all_breaches = []
    for p in providers:
        if p.is_available():
            import asyncio
            result = asyncio.run(p.check_email(email))
            if result.success:
                all_breaches.extend([(b.name, b.year) for b in result.breaches])

    seen = set()
    unique = []
    for name, year in all_breaches:
        if name not in seen:
            seen.add(name)
            unique.append({"name": name, "year": year})

    return {
        "email": email,
        "breach_count": len(unique),
        "breaches": unique,
    }
