"""
Beveiligingsheaders die Django's SecurityMiddleware niet zelf zet:
Content-Security-Policy en Permissions-Policy.

CSP staat bewust inline styles/scripts toe ('unsafe-inline'): de pagina's gebruiken
inline <style>-blokken, JSON-LD en een inline font-`onload`-handler. De winst zit in
het beperken van de herkomst (default-src 'self'), het blokkeren van plug-ins/objects
en framing, en het vastzetten van base-uri/form-action — dat dicht het grootste deel
van de XSS-/clickjacking-/injectie-oppervlakte zonder de SSR-opzet te breken.

Configureerbaar via env: CSP_ENABLED (default aan), CSP_REPORT_ONLY (default uit).
"""
import os

# Externe bronnen die de pagina's nodig hebben (alleen Google Fonts).
_CSP = "; ".join([
    "default-src 'self'",
    "base-uri 'self'",
    "object-src 'none'",
    "frame-ancestors 'none'",
    "form-action 'self'",
    "img-src 'self' data: https:",
    "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
    "font-src 'self' https://fonts.gstatic.com data:",
    "script-src 'self' 'unsafe-inline'",
    "connect-src 'self'",
])

_PERMISSIONS = ", ".join([
    "geolocation=()", "microphone=()", "camera=()", "payment=()",
    "usb=()", "magnetometer=()", "gyroscope=()", "browsing-topics=()",
])


def _enabled(name, default):
    return os.getenv(name, default).strip().lower() in ("1", "true", "yes", "on")


class SecurityHeadersMiddleware:
    """Zet CSP + Permissions-Policy op elke response (idempotent: overschrijft niet
    als er al expliciet een is gezet, bv. door een specifieke view)."""

    def __init__(self, get_response):
        self.get_response = get_response
        self.enabled = _enabled("CSP_ENABLED", "True")
        self.report_only = _enabled("CSP_REPORT_ONLY", "False")
        self.header = ("Content-Security-Policy-Report-Only" if self.report_only
                       else "Content-Security-Policy")

    def __call__(self, request):
        response = self.get_response(request)
        if self.enabled and "Content-Security-Policy" not in response \
                and "Content-Security-Policy-Report-Only" not in response:
            response[self.header] = _CSP
        response.setdefault("Permissions-Policy", _PERMISSIONS)
        return response
