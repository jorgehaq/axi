from typing import Any
from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context) -> Response | None:
    response = drf_exception_handler(exc, context)
    if response is None:
        return Response({"error": {"code": "server_error", "message": str(exc)}},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    detail = response.data
    if isinstance(detail, dict) and "detail" in detail:
        detail = {"message": detail["detail"]}

    response.data = {"error": {
        "code": _status_code_to_code(response.status_code),
        "message": _extract_message(detail),
        "details": detail if isinstance(detail, dict) else None
    }}
    return response


def _status_code_to_code(st: int) -> str:
    if st == 400: return "bad_request"
    if st == 401: return "unauthorized"
    if st == 403: return "forbidden"
    if st == 404: return "not_found"
    if st == 422: return "unprocessable_entity"
    if st >= 500: return "server_error"
    return "error"


def _extract_message(detail: Any) -> str:
    if isinstance(detail, dict) and "message" in detail:
        return str(detail["message"])
    return "Request failed"

