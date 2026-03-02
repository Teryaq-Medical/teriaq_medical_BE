from django.conf import settings
def set_auth_cookie(response, token_key):
    response.set_cookie(
        key="auth_token",
        value=token_key,
        httponly=True,
        # In production (DEBUG=False), these must be True and "None"
        secure=not settings.DEBUG, 
        samesite="Lax" if settings.DEBUG else "None",
        max_age=60 * 60 * 24 * 7 # 7 days
    )