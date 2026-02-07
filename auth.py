from jose import jwt
import httpx

KEYCLOAK_REALM = "myfirstrealm"
KEYCLOAK_URL = "http://localhost:8080"
CLIENT_ID = "fastapi-client"

JWKS_URL = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}/protocol/openid-connect/certs"
ISSUER = f"{KEYCLOAK_URL}/realms/{KEYCLOAK_REALM}"

jwks = httpx.get(JWKS_URL).json()

def verify_token(token: str):
    return jwt.decode(
        token,
        jwks,
        algorithms=["RS256"],
        audience="account",
        issuer=ISSUER,
    )



