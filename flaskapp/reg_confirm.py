from itsdangerous import URLSafeSerializer
from app import app


def generete_token(email):
    serializer = URLSafeSerializer(app.secret_key)
    return serializer.dumps(email, salt=app.secret_key)


def confirm(token, expiration=3600):
    serializer = URLSafeSerializer(app.secret_key)
    try:
        email = serializer.loads(
            token,
            salt=app.security_key,
            expiration=3600
        )
    except Exception as e:
        return False
        print(e)
    return email
