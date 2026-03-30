import ipaddress
from urllib.parse import urlparse

from fastapi import HTTPException, status

from app.core.config import settings

BLOCKED_HOSTS = {"localhost", "127.0.0.1", "0.0.0.0"}


def validate_embeddable_url(url: str) -> None:
    parsed = urlparse(url)
    if parsed.scheme != "https":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only https URLs are allowed")

    hostname = (parsed.hostname or "").lower()
    if not hostname or hostname in BLOCKED_HOSTS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Host is not allowed")

    try:
        ip_obj = ipaddress.ip_address(hostname)
        if ip_obj.is_private or ip_obj.is_loopback or ip_obj.is_multicast:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Private or loopback hosts are blocked")
    except ValueError:
        pass

    allowlist = [domain.strip().lower() for domain in settings.embeddable_url_allowlist.split(",") if domain.strip()]

    allowed = any(hostname == domain or hostname.endswith(f".{domain}") for domain in allowlist)
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"URL domain is not in allowlist: {hostname}",
        )
