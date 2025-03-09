from django.http import JsonResponse

from config import settings


def lockout_response(request, credentials):
    """
    Custom response when a user is locked out due to too many failed login attempts.
    """
    status = getattr(settings, "AXES_HTTP_RESPONSE_CODE", 429)
    message = (
        "Too many failed login attempts,"
        " Your account has been temporarily locked."
        " Please try again later."
    )

    return JsonResponse(
        {
            "message": message,
            "errors": {
                "detail": message,
            },
            "status_code": status,
        },
        status=status,
    )
