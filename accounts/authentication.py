from rest_framework.authentication import TokenAuthentication

class CookieTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        # Skip auth for registration endpoints
        if request.path.startswith("/api/register/"):
            return None

        token = request.COOKIES.get("auth_token")
        if not token:
            return None

        return self.authenticate_credentials(token)
