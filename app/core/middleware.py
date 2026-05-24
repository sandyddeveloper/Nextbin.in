import uuid
import json
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
        
        # Check if the route is bypassed or is an OPTIONS preflight request
        if request.method == "OPTIONS" or path in BYPASS_ROUTES or path.startswith("/docs") or path.startswith("/redoc") or "/nilagravity/vault/approve" in path:
            request.state.platform = request.headers.get("X-Platform", "unknown")
            return await call_next(request)
            
        platform = request.headers.get("X-Platform")
        valid_platforms = ["web", "ios", "android"]
        
        if not platform:
            logger.warning(f"Rejected request to {path}: Missing X-Platform header")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": "failed",
                    "message": "X-Platform header is required for secure endpoints. Must be one of: 'web', 'ios', 'android'.",
                    "errors": None
                }
            )
            
        if platform not in valid_platforms:
            logger.warning(f"Rejected request to {path}: Invalid X-Platform header '{platform}'")
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "status": "failed",
                    "message": f"Invalid X-Platform value '{platform}'. Must be one of: 'web', 'ios', 'android'.",
                    "errors": None
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


class ResponseStandardizationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to automatically wrap success and error JSON responses under the API prefix
    in the standard structure: {"status": ..., "message": ..., "data": ...} or {"status": ..., "message": ..., "errors": ...}.
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        path = request.url.path
        # Only standardize JSON responses for API routes (exclude static docs/openapi)
        if (
            path.startswith("/api/")
            and response.headers.get("content-type") == "application/json"
            and not path.endswith("openapi.json")
        ):
            # Consume response body to inspect/wrap
            body_parts = []
            async for chunk in response.body_iterator:
                body_parts.append(chunk)
            body = b"".join(body_parts)
            
            try:
                data = json.loads(body.decode("utf-8"))
                
                # If already standardized (has "status" and "message"), do not double-wrap
                if isinstance(data, dict) and "status" in data and "message" in data:
                    async def body_iterator():
                        yield body
                    response.body_iterator = body_iterator()
                    return response
                
                # Standardize shape
                status_code = response.status_code
                status_label = "success" if 200 <= status_code < 300 else "failed"
                
                wrapped_data = {
                    "status": status_label,
                    "message": "Operation successful" if 200 <= status_code < 300 else "An error occurred",
                    "data" if 200 <= status_code < 300 else "errors": data
                }
                
                # Exclude original Content-Length since the body content is wrapped and its size has changed
                headers = {k: v for k, v in response.headers.items() if k.lower() != "content-length"}
                new_response = JSONResponse(
                    content=wrapped_data,
                    status_code=status_code,
                    headers=headers
                )
                return new_response
                
            except Exception:
                # Fallback to original response on parse failure
                async def body_iterator():
                    yield body
                response.body_iterator = body_iterator()
                return response
                
        return response
