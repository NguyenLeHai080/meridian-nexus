import argparse
import json
import ssl
from http.client import HTTPConnection, HTTPSConnection
from urllib.parse import urlparse

LOCAL_HOSTS = {"localhost", "127.0.0.1", "::1"}


def request(target: str, path: str) -> tuple[int, dict[str, str], bytes]:
    parsed = urlparse(target)
    host = parsed.hostname
    if host is None:
        raise ValueError("Target must contain a hostname")

    if parsed.scheme == "https":
        connection = HTTPSConnection(
            host, parsed.port or 443, timeout=15, context=ssl.create_default_context()
        )
    elif parsed.scheme == "http" and host in LOCAL_HOSTS:
        connection = HTTPConnection(host, parsed.port or 80, timeout=15)
    else:
        raise ValueError("Remote smoke targets must use HTTPS")

    base_path = parsed.path.rstrip("/")
    connection.request("GET", f"{base_path}{path}", headers={"Accept": "application/json"})
    response = connection.getresponse()
    body = response.read()
    headers = {name.lower(): value for name, value in response.getheaders()}
    connection.close()
    return response.status, headers, body


def main() -> None:
    parser = argparse.ArgumentParser(description="Read-only deployment smoke tests")
    parser.add_argument("--target", required=True)
    args = parser.parse_args()

    health_status, health_headers, health_body = request(args.target, "/health")
    product_status, _, _ = request(args.target, "/api/v1/storefront/products")

    checks = {
        "health_status": health_status == 200,
        "product_status": product_status == 200,
        "nosniff": health_headers.get("x-content-type-options") == "nosniff",
        "csp": bool(health_headers.get("content-security-policy")),
        "server_hidden": "server" not in health_headers,
    }

    try:
        health_payload = json.loads(health_body)
        checks["health_payload"] = health_payload.get("data", {}).get("status") == "ok"
    except json.JSONDecodeError:
        checks["health_payload"] = False

    print(json.dumps({"target": args.target, "checks": checks}, indent=2))
    if not all(checks.values()):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
