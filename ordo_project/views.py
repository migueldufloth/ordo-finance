from django.db import connection
from django.http import JsonResponse


def health(request):
    try:
        connection.ensure_connection()
        db_ok = True
    except Exception:
        db_ok = False

    status = "ok" if db_ok else "degraded"
    return JsonResponse(
        {"status": status, "database": "ok" if db_ok else "error"},
        status=200 if db_ok else 503,
    )
