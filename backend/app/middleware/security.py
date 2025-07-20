"""
Security middleware for FastAPI.

This middleware adds various security headers and protections to the application,
including Content Security Policy (CSP), HTTP Strict Transport Security (HSTS),
and other security-related headers.
"""
import re
from typing import Any, Dict, List, Optional, Pattern, Set, Tuple, Union

from fastapi import FastAPI, Request, Response
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that adds security headers to all responses."""
    
    def __init__(
        self,
        app: ASGIApp,
        csp_directives: Optional[Dict[str, Union[str, List[str]]]] = None,
        feature_policy: Optional[Dict[str, Union[str, List[str]]]] = None,
        permissions_policy: Optional[Dict[str, Union[str, List[str]]]] = None,
        referrer_policy: str = "strict-origin-when-cross-origin",
        x_content_type_options: str = "nosniff",
        x_frame_options: str = "DENY",
        x_xss_protection: str = "1; mode=block",
        strict_transport_security: str = "max-age=31536000; includeSubDomains",
        expect_ct: Optional[str] = None,
        x_permitted_cross_domain_policies: str = "none",
        cross_origin_opener_policy: str = "same-origin",
        cross_origin_resource_policy: str = "same-origin",
        cross_origin_embedder_policy: str = "require-corp",
        content_security_policy_report_only: bool = False,
    ) -> None:
        """Initialize the security headers middleware.
        
        Args:
            app: The ASGI application.
            csp_directives: Content Security Policy directives.
            feature_policy: Feature Policy directives (deprecated, use permissions_policy).
            permissions_policy: Permissions Policy directives.
            referrer_policy: Referrer-Policy header value.
            x_content_type_options: X-Content-Type-Options header value.
            x_frame_options: X-Frame-Options header value.
            x_xss_protection: X-XSS-Protection header value.
            strict_transport_security: Strict-Transport-Security header value.
            expect_ct: Expect-CT header value.
            x_permitted_cross_domain_policies: X-Permitted-Cross-Domain-Policies header value.
            cross_origin_opener_policy: Cross-Origin-Opener-Policy header value.
            cross_origin_resource_policy: Cross-Origin-Resource-Policy header value.
            cross_origin_embedder_policy: Cross-Origin-Embedder-Policy header value.
            content_security_policy_report_only: Whether to use Content-Security-Policy-Report-Only.
        """
        super().__init__(app)
        
        # Default CSP directives
        self.csp_directives = {
            "default-src": ["'self'"],
            "script-src": ["'self'"],
            "style-src": ["'self'"],
            "img-src": ["'self'"],
            "font-src": ["'self'"],
            "connect-src": ["'self'"],
            "frame-src": ["'self'"],
            "object-src": ["'none'"],
            "base-uri": ["'self'"],
            "form-action": ["'self'"],
            "frame-ancestors": ["'none'"],
            "block-all-mixed-content": [],
            "upgrade-insecure-requests": [],
        }
        
        # Development-specific CSP directives
        if is_development:
            self.csp_directives.update({
                "script-src": [
                    "'self'",
                    "'unsafe-inline'",
                    "'unsafe-eval'"
                ],
                "style-src": [
                    "'self'",
                    "'unsafe-inline'"
                ],
                "img-src": [
                    "'self'",
                    "data:",
                    "blob:",
                    "https:",
                    "http:"
                ],
                "font-src": [
                    "'self'",
                    "data:",
                    "https:",
                    "http:"
                ],
                "connect-src": [
                    "'self'",
                    "ws:",
                    "wss:",
                    "http:",
                    "https:"
                ]
            })
        
        # Update with user-provided directives
        if csp_directives:
            for key, value in csp_directives.items():
                if isinstance(value, str):
                    self.csp_directives[key] = [value]
                else:
                    self.csp_directives[key] = value
        
        # Feature Policy (deprecated, but kept for backwards compatibility)
        self.feature_policy = feature_policy or {
            "accelerometer": ["'none'"],
            "camera": ["'none'"],
            "geolocation": ["'none'"],
            "gyroscope": ["'none'"],
            "magnetometer": ["'none'"],
            "microphone": ["'none'"],
            "payment": ["'none'"],
            "usb": ["'none'"],
        }
        
        # Permissions Policy (replaces Feature Policy)
        self.permissions_policy = permissions_policy or {
            "accelerometer": ["'none'"],
            "ambient-light-sensor": ["'none'"],
            "autoplay": ["'none'"],
            "battery": ["'none'"],
            "camera": ["'none'"],
            "display-capture": ["'none'"],
            "document-domain": ["'none'"],
            "encrypted-media": ["'none'"],
            "execution-while-not-rendered": ["'none'"],
            "execution-while-out-of-viewport": ["'none'"],
            "fullscreen": ["'none'"],
            "geolocation": ["'none'"],
            "gyroscope": ["'none'"],
            "keyboard-map": ["'none'"],
            "magnetometer": ["'none'"],
            "microphone": ["'none'"],
            "midi": ["'none'"],
            "navigation-override": ["'none'"],
            "payment": ["'none'"],
            "picture-in-picture": ["'none'"],
            "publickey-credentials-get": ["'none'"],
            "screen-wake-lock": ["'none'"],
            "sync-xhr": ["'none'"],
            "usb": ["'none'"],
            "web-share": ["'none'"],
            "xr-spatial-tracking": ["'none'"],
        }
        
        # Other security headers
        self.referrer_policy = referrer_policy
        self.x_content_type_options = x_content_type_options
        self.x_frame_options = x_frame_options
        self.x_xss_protection = x_xss_protection
        self.strict_transport_security = strict_transport_security
        self.expect_ct = expect_ct
        self.x_permitted_cross_domain_policies = x_permitted_cross_domain_policies
        self.cross_origin_opener_policy = cross_origin_opener_policy
        self.cross_origin_resource_policy = cross_origin_resource_policy
        self.cross_origin_embedder_policy = cross_origin_embedder_policy
        self.content_security_policy_report_only = content_security_policy_report_only
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request and add security headers to the response."""
        # Process the request
        response = await call_next(request)
        
        # Add security headers
        self._add_security_headers(request, response)
        
        return response
    
    def _add_security_headers(self, request: Request, response: Response) -> None:
        """Add security headers to the response."""
        # Content Security Policy
        csp_parts = []
        for directive, sources in self.csp_directives.items():
            if sources:
                csp_parts.append(f"{directive} {' '.join(sources)}")
            else:
                csp_parts.append(directive)
        
        csp_header = "; ".join(csp_parts)
        
        if self.content_security_policy_report_only:
            response.headers["Content-Security-Policy-Report-Only"] = csp_header
        else:
            response.headers["Content-Security-Policy"] = csp_header
        
        # Feature Policy (deprecated)
        feature_policy_parts = []
        for feature, origins in self.feature_policy.items():
            feature_policy_parts.append(f"{feature} {' '.join(origins)}")
        
        response.headers["Feature-Policy"] = ", ".join(feature_policy_parts)
        
        # Permissions Policy
        permissions_policy_parts = []
        for feature, origins in self.permissions_policy.items():
            permissions_policy_parts.append(f"{feature}=({' '.join(origins)})")
        
        response.headers["Permissions-Policy"] = ", ".join(permissions_policy_parts)
        
        # Other security headers
        response.headers["Referrer-Policy"] = self.referrer_policy
        response.headers["X-Content-Type-Options"] = self.x_content_type_options
        response.headers["X-Frame-Options"] = self.x_frame_options
        response.headers["X-XSS-Protection"] = self.x_xss_protection
        
        # Only add HSTS if the request was made over HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = self.strict_transport_security
        
        if self.expect_ct:
            response.headers["Expect-CT"] = self.expect_ct
        
        response.headers["X-Permitted-Cross-Domain-Policies"] = self.x_permitted_cross_domain_policies
        response.headers["Cross-Origin-Opener-Policy"] = self.cross_origin_opener_policy
        response.headers["Cross-Origin-Resource-Policy"] = self.cross_origin_resource_policy
        response.headers["Cross-Origin-Embedder-Policy"] = self.cross_origin_embedder_policy


class SecureHostMiddleware(BaseHTTPMiddleware):
    """Middleware that enforces the use of secure hosts."""
    
    def __init__(
        self,
        app: ASGIApp,
        allowed_hosts: Optional[List[str]] = None,
        www_redirect: bool = True,
        www_prefix: str = "www",
        https_redirect: bool = True,
        https_port: int = 443,
        https_ports: Optional[List[int]] = None,
    ) -> None:
        """Initialize the secure host middleware."""
        super().__init__(app)
        
        # Default allowed hosts
        self.allowed_hosts = ["localhost", "127.0.0.1"]
        if allowed_hosts:
            self.allowed_hosts.extend(allowed_hosts)
        
        # Compile regex patterns for host matching
        self.allowed_hosts_patterns = []
        for host in self.allowed_hosts:
            # Escape dots in the hostname
            pattern = host.replace(".", r"\\.")
            # Allow subdomains if the host starts with a dot
            if host.startswith("."):
                pattern = r"(.*\\.)??" + pattern[1:]
            self.allowed_hosts_patterns.append(re.compile(f"^{pattern}$", re.IGNORECASE))
        
        self.www_redirect = www_redirect
        self.www_prefix = www_prefix
        self.https_redirect = https_redirect
        self.https_port = https_port
        self.https_ports = https_ports or [443, 8443]
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request and enforce secure hosts."""
        # Get the host and port from the request
        host_header = request.headers.get("host", "")
        host = host_header.split(":")[0]
        port = int(host_header.split(":")[1]) if ":" in host_header else None
        
        # Check if the host is allowed
        if not self._is_allowed_host(host):
            return Response(
                content="Invalid host header",
                status_code=400,
                headers={"Content-Type": "text/plain"},
            )
        
        # Handle www redirect
        if self.www_redirect and not host.startswith(f"{self.www_prefix}.") and host != "localhost":
            url = request.url.replace(
                netloc=f"{self.www_prefix}.{host}",
                scheme="https" if self.https_redirect else request.url.scheme,
            )
            return Response(
                status_code=301,
                headers={"Location": str(url)},
            )
        
        # Handle HTTPS redirect
        if self.https_redirect and request.url.scheme != "https":
            url = request.url.replace(
                scheme="https",
                port=self.https_port,
            )
            return Response(
                status_code=301,
                headers={"Location": str(url)},
            )
        
        # Process the request
        return await call_next(request)
    
    def _is_allowed_host(self, host: str) -> bool:
        """Check if the host is allowed."""
        # Allow localhost and IP addresses in development
        if settings.DEBUG and (host == "localhost" or re.match(r"^\d+\.\d+\.\d+\.\d+$", host)):
            return True
        
        # Check against allowed hosts patterns
        for pattern in self.allowed_hosts_patterns:
            if pattern.match(host):
                return True
        
        return False


def setup_security_middleware(app: FastAPI, is_development: bool = False) -> None:
    """Set up security middleware for the FastAPI application.
    
    Args:
        app: The FastAPI application instance
        is_development: Whether the application is running in development mode
    """
    # Add security headers middleware with development flag
    app.add_middleware(SecurityHeadersMiddleware, is_development=is_development)
    
    # Add secure host middleware
    if settings.ENVIRONMENT == "production":
        app.add_middleware(
            SecureHostMiddleware,
            allowed_hosts=settings.ALLOWED_HOSTS,
            https_redirect=True,
            www_redirect=True,
        )
    
    # Add HTTPS redirect middleware
    if settings.ENVIRONMENT == "production" and settings.FORCE_HTTPS:
        app.add_middleware(HTTPSRedirectMiddleware)
