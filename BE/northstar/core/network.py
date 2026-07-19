from ipaddress import ip_address, ip_network

from fastapi import Request

from northstar.core.config import get_settings


def _is_trusted_proxy(address: str) -> bool:
    try:
        client = ip_address(address)
    except ValueError:
        return False
    for configured_network in get_settings().trusted_proxy_networks:
        try:
            if client in ip_network(configured_network, strict=False):
                return True
        except ValueError:
            continue
    return False


def client_ip(request: Request) -> str:
    peer = request.client.host if request.client is not None else "unknown"
    if not _is_trusted_proxy(peer):
        return peer
    forwarded_for = request.headers.get("X-Forwarded-For", "")
    candidate = forwarded_for.split(",", 1)[0].strip()
    try:
        return str(ip_address(candidate))
    except ValueError:
        return peer
