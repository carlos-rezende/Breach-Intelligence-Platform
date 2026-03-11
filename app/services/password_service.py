"""Serviço de verificação de senha via Pwned Passwords API."""

import hashlib

import httpx

PWNED_PASSWORDS_URL = "https://api.pwnedpasswords.com/range"


async def check_password(password: str) -> tuple[bool, int]:
    """
    Verifica se a senha apareceu em vazamentos usando k-anonymity.
    A senha nunca é enviada - apenas o hash SHA-1 (parcial).
    Retorna (pwned, count).
    """
    sha1 = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{PWNED_PASSWORDS_URL}/{prefix}")

        if response.status_code != 200:
            raise httpx.HTTPStatusError(
                f"Pwned Passwords API retornou {response.status_code}",
                request=response.request,
                response=response,
            )

        for line in response.text.strip().splitlines():
            parts = line.split(":")
            if len(parts) == 2 and parts[0].strip() == suffix:
                return True, int(parts[1].strip())

    return False, 0
