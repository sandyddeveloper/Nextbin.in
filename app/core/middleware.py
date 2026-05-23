import uuid
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger("nextbin.api.middleware")

# List of routes that are bypassed from mandatory platform checks (docs, OpenAPI specification, root health check)
BYPASS_ROUTES = [
    "/",
    "/docs",
    "/redoc",
    "/api/v1/openapi.json",
    "/deploy",
]

class RequestIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware to attach a unique X-Request-ID to every request context.
    Propagates the ID to client response headers.
    """
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID")
        if not request_id:
            request_id = str(uuid.uuid4())
            
        request.state.request_id = request_id
        
        # Process the request
        response = await call_next(request)
        
        # Inject Request ID to response headers
        response.headers["X-Request-ID"] = request_id
        return response

class PlatformValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce X-Platform validation for all secure API endpoints.
    Allows access only from verified client distributions (web, ios, android).
    """
    async def dispatch(self, request: Request, call_next):
        # Resolve path
        path = request.url.path
        
        # Check if the route is bypassed
        if path in BYPASS_ROUTES or path.startswith("/docs") or path.startswith("/redoc"):
            request.state.platform = request.headers.get("X-Platform", "unknown")
            return await call_next(request)
            
        platform = request.headers.get("X-Platform")
        valid_platforms = ["web", "ios", "android"]
        
        if not platform:
            logger.warning(f"Rejected request to {path}: Missing X-Platform header")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": "X-Platform header is required for secure endpoints. "
                              "Must be one of: 'web', 'ios', 'android'."
                }
            )
            
        if platform not in valid_platforms:
            logger.warning(f"Rejected request to {path}: Invalid X-Platform header '{platform}'")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "detail": f"Invalid X-Platform value '{platform}'. Must be one of: 'web', 'ios', 'android'."
                }
            )
            
        request.state.platform = platform
        return await call_next(request)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to inject standard security HTTP headers (Anti-Clickjacking, Anti-XSS, MIME sniffing).
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "no-referrer-when-downgrade"
        return response
