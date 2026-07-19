import argparse
import http.client
import json
import sys
from http.cookies import SimpleCookie
from urllib.parse import urlencode, urlparse

ALLOWED_TARGETS = {"localhost", "127.0.0.1", "::1"}
TRUSTED_ORIGIN = "http://localhost:5173"


def request(
    connection: http.client.HTTPConnection,
    method: str,
    path: str,
    *,
    headers: dict[str, str] | None = None,
    body: bytes | None = None,
) -> tuple[int, dict[str, str], bytes]:
    connection.request(method, path, body=body, headers=headers or {})
    response = connection.getresponse()
    response_body = response.read()
    response_headers = {name.lower(): value for name, value in response.getheaders()}
    return response.status, response_headers, response_body


def csrf_session(
    connection: http.client.HTTPConnection,
) -> tuple[str, dict[str, str]]:
    connection.request("GET", "/sanctum/csrf-cookie")
    response = connection.getresponse()
    response.read()
    cookies = SimpleCookie()
    for name, value in response.getheaders():
        if name.lower() == "set-cookie":
            cookies.load(value)
    token = cookies["XSRF-TOKEN"].value
    return token, {
        "Origin": TRUSTED_ORIGIN,
        "X-XSRF-TOKEN": token,
        "Cookie": f"XSRF-TOKEN={token}",
        "Content-Type": "application/json",
    }


def json_body(payload: dict[str, object]) -> bytes:
    return json.dumps(payload, separators=(",", ":")).encode()


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Non-destructive Northstar API security smoke test"
    )
    parser.add_argument("--target", default="http://127.0.0.1:8000")
    args = parser.parse_args()
    target = urlparse(args.target)
    if target.scheme != "http" or target.hostname not in ALLOWED_TARGETS:
        raise SystemExit("Refusing to test anything except a local HTTP target.")

    connection = http.client.HTTPConnection(target.hostname, target.port or 80, timeout=20)
    results: list[dict[str, object]] = []

    def check(name: str, expected: int | bool, actual: int | bool) -> None:
        results.append(
            {"test": name, "expected": expected, "actual": actual, "passed": expected == actual}
        )

    status, _, _ = request(connection, "GET", "/health", headers={"Host": "attacker.example"})
    check("host_header_injection", 400, status)

    login_payload = json_body({"email": "nobody@example.com", "password": "WrongPassword123!"})
    status, _, _ = request(
        connection,
        "POST",
        "/api/v1/auth/login",
        headers={"Content-Type": "application/json"},
        body=login_payload,
    )
    check("untrusted_origin", 403, status)

    status, _, _ = request(
        connection,
        "POST",
        "/api/v1/auth/login",
        headers={"Origin": TRUSTED_ORIGIN, "Content-Type": "application/json"},
        body=login_payload,
    )
    check("missing_csrf", 419, status)

    status, _, _ = request(connection, "GET", "/api/v1/admin/dashboard")
    check("unauthenticated_admin", 401, status)

    status, _, _ = request(
        connection,
        "GET",
        "/api/v1/auth/me",
        headers={"Cookie": "northstar_session=tampered-token"},
    )
    check("tampered_session", 401, status)

    query = urlencode({"search": "' OR '1'='1"})
    status, _, _ = request(connection, "GET", f"/api/v1/storefront/products?{query}")
    check("sql_injection", 200, status)

    status, _, _ = request(connection, "GET", "/api/v1/storefront/posts/..%2F..%2F.env")
    check("path_traversal_rejected", True, status in {404, 422})

    status, _, _ = request(connection, "TRACE", "/health")
    check("trace_method", 403, status)

    _, _, _ = request(connection, "GET", "/health")
    token, protected_headers = csrf_session(connection)
    large_payload = json_body(
        {
            "name": "Tester",
            "email": "large@example.com",
            "subject": "Oversized",
            "message": "x" * 1_100_000,
        }
    )
    status, _, _ = request(
        connection,
        "POST",
        "/api/v1/storefront/contact",
        headers=protected_headers,
        body=large_payload,
    )
    check("request_size_limit", 413, status)

    brute_payload = json_body(
        {"email": "live-pentest@example.com", "password": "WrongPassword123!"}
    )
    brute_status = 0
    for _attempt in range(9):
        brute_status, _, _ = request(
            connection,
            "POST",
            "/api/v1/auth/login",
            headers=protected_headers,
            body=brute_payload,
        )
    check("login_rate_limit", 429, brute_status)

    status, headers, _ = request(connection, "GET", "/health")
    check("health_after_attack_payloads", 200, status)
    check("content_security_policy", True, "content-security-policy" in headers)
    check("nosniff", "nosniff", headers.get("x-content-type-options", ""))
    check("server_header_removed", False, "server" in headers)

    print(
        json.dumps(
            {"target": args.target, "csrf_token_length": len(token), "results": results}, indent=2
        )
    )
    return 0 if all(bool(item["passed"]) for item in results) else 1


if __name__ == "__main__":
    sys.exit(main())
