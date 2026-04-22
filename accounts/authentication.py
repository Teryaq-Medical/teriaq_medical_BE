from rest_framework.authentication import BaseAuthentication, TokenAuthentication
from rest_framework.authtoken.models import Token

class CookieTokenAuthentication(BaseAuthentication):
    """
    Authentication that checks:
    1. Cookie named 'auth_token'
    2. Authorization header (Bearer or Token)
    """
    def authenticate(self, request):
        token_key = None

        # 1. Try cookie first
        token_key = request.COOKIES.get("auth_token")

        # 2. If not in cookie, try Authorization header
        if not token_key:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            if auth_header.startswith('Token '):
                token_key = auth_header[6:].strip()
            elif auth_header.startswith('Bearer '):
                token_key = auth_header[7:].strip()

        if not token_key:
            return None

        try:
            token = Token.objects.get(key=token_key)
        except Token.DoesNotExist:
            return None

        return (token.user, token)