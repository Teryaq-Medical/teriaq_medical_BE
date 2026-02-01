def set_auth_cookie(response, token):
    response.set_cookie(
        key='auth_token',
        value=token,
        httponly=True,
        secure=False,   # خليها True في production
        samesite='Lax',
        max_age=60 * 60 * 24 * 7  # أسبوع
    )
