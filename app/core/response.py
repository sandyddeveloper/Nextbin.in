from fastapi.responses import JSONResponse
from fastapi import status, Request
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError as PydanticValidationError
import traceback
from app.core.config import settings

class APIResponse(JSONResponse):
    """
    Standardized API Response Class for FastAPI.
    
    Usage:
        return APIResponse(data=user_data, message="User created", status_code=201)
        return APIResponse(errors=serializer.errors, message="Validation failed", status_code=400)
    """
    def __init__(self, data=None, errors=None, message=None, status_code=status.HTTP_200_OK, **kwargs):
        
        # 1. Determine Status Label (success/error)
        # Any 2xx code is 'success', anything else is 'error' or 'failed'
        if 200 <= status_code < 300:
            status_label = "success"
            default_message = "Operation successful"
            content_key = "data"
            content_value = data
        else:
            status_label = "failed"
            default_message = "An error occurred"
            content_key = "errors"
            content_value = errors if errors is not None else data # Fallback if someone passes error data as 'data'

        # 2. Build the Standard Structure
        output_data = {
            "status": status_label,
            "message": message or default_message,
            content_key: content_value
        }

        # 3. Initialize the actual FastAPI JSONResponse
        super().__init__(content=output_data, status_code=status_code, **kwargs)


async def custom_exception_handler(request: Request, exc: Exception) -> APIResponse:
    """
    UX-Optimized & Secure Exception Handler for FastAPI.
    """
    # 1. Convert/Handle Validation Errors (Pydantic / RequestValidationError)
    if isinstance(exc, (RequestValidationError, PydanticValidationError)):
        errors = None
        message = "Validation failed"
        
        if isinstance(exc, RequestValidationError):
            raw_errors = exc.errors()
            err_dict = {}
            for err in raw_errors:
                loc = err.get("loc", [])
                field_name = str(loc[-1]) if loc else "field"
                msg = err.get("msg", "Invalid value")
                if field_name not in err_dict:
                    err_dict[field_name] = []
                err_dict[field_name].append(msg)
            
            errors = err_dict
            
            # Format friendly message using first field validation issue
            first_key = next(iter(err_dict), None)
            if first_key:
                first_err = err_dict[first_key]
                val = first_err[0] if isinstance(first_err, list) else first_err
                clean_field = str(first_key).replace("_", " ").title()
                message = f"{clean_field}: {val}"
        else:
            errors = exc.errors()
            message = str(exc)

        return APIResponse(
            message=message,
            errors=errors,
            status_code=status.HTTP_400_BAD_REQUEST
        )

    # 2. Handle HTTPExceptions
    if isinstance(exc, StarletteHTTPException):
        status_code = exc.status_code
        errors = exc.detail
        message = "Request failed"

        # --- UX MAPPING ---
        if status_code == 404:
            message = "The requested data could not be found."

        elif status_code == 401:
            message = "Your session has expired. Please log in again."

        elif status_code == 403:
            message = "You do not have permission to perform this action."

        elif status_code == 429:
            wait_time = getattr(exc, "wait", None)
            if wait_time:
                message = f"Too many attempts. Please wait {int(wait_time)} seconds before trying again."
            else:
                retry_after = request.headers.get("Retry-After")
                if retry_after:
                    message = f"Too many attempts. Please wait {retry_after} seconds before trying again."
                else:
                    message = "Too many attempts. Please wait a moment and try again."  

        elif status_code == 400:
            if isinstance(errors, dict):
                if "detail" in errors:
                    message = str(errors["detail"])
                else:
                    first_key = next(iter(errors), None)
                    if first_key:
                        first_err = errors[first_key]
                        val = first_err[0] if isinstance(first_err, list) else first_err
                        clean_field = str(first_key).replace("_", " ").title()
                        message = f"{clean_field}: {val}"
            elif isinstance(errors, list) and errors:
                message = str(errors[0])
            else:
                message = str(errors)

        else:
            if isinstance(errors, dict) and "detail" in errors:
                message = str(errors["detail"])
            else:
                message = str(errors)

        # Wrap details as dict
        errors_payload = errors
        if isinstance(errors, str):
            errors_payload = {"detail": errors}

        return APIResponse(
            message=message,
            errors=errors_payload,
            status_code=status_code
        )

    # --- UNHANDLED EXCEPTIONS (500) ---
    if settings.DEBUG:
        tb = traceback.format_exception(type(exc), exc, exc.__traceback__)[-5:]
        message = f"Server Crash: {exc.__class__.__name__}"
        errors = {
            "type": exc.__class__.__name__,
            "detail": str(exc),
            "traceback": tb
        }
    else:
        message = "An unexpected error occurred. Our team has been notified."
        errors = {}

    custom_response = APIResponse(
        message=message,
        errors=errors,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

    custom_response._raw_exc = exc

    # Try reporting to AdminNotificationService if available
    try:
        from apps.notification.service import AdminNotificationService
        AdminNotificationService.report_error(
            request=request,
            exc=exc,
            error_details=errors
        )
    except ImportError:
        pass

    return custom_response
