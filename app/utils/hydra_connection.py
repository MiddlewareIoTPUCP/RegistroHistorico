from fastapi import Depends
from fastapi.security import OAuth2AuthorizationCodeBearer, SecurityScopes
from jose import jwt
from httpx import AsyncClient

from app.config import get_settings


class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


settings = get_settings()
hydra_scheme = OAuth2AuthorizationCodeBearer(authorizationUrl=settings.hydra_url+"/oauth2/auth",
                                             tokenUrl=settings.hydra_url+"/oauth2/token",
                                             scopes={"all": "Get all information"})


async def get_current_token(security_scopes: SecurityScopes, token: str = Depends(hydra_scheme)) -> dict:
    async with AsyncClient() as session:
        resp = await session.get(settings.hydra_url + "/.well-known/jwks.json")
        jwks = resp.json()
        unverified_header = jwt.get_unverified_header(token)

        rsa_key = dict()
        for key in jwks["keys"]:
            if key["kid"] == unverified_header["kid"]:
                rsa_key = {
                    "kty": key["kty"],
                    "kid": key["kid"],
                    "use": key["use"],
                    "n": key["n"],
                    "e": key["e"],
                }

        if rsa_key:
            try:
                payload = jwt.decode(
                    token,
                    rsa_key,
                    audience="",
                    algorithms=settings.hydra_algorithms,
                    issuer=settings.hydra_url + "/",
                    options={'verify_aud': False}
                )
            except jwt.ExpiredSignatureError as e:
                raise AuthError(
                    {
                        "code": "token_expired",
                        "description": "Token is expired",
                        "error": str(e)
                    },
                    401
                )
            except jwt.JWTClaimsError as e:
                raise AuthError(
                    {
                        "code": "invalid_claims",
                        "description": "Incorrect claims, please check the audience and issuer",
                        "error": str(e)
                    },
                    401,
                )
            except Exception as e:
                raise AuthError(
                    {
                        "code": "invalid_header",
                        "description": "Unable to parse authentication token.",
                        "error": str(e)
                    },
                    401,
                )

            token_scopes = payload.get("scp", "")
            for scope in security_scopes.scopes:
                if scope not in token_scopes:
                    raise AuthError(
                        {
                            "code": "Unauthorized",
                            "description": "You don't have access to this resource. {} scopes required".format(
                                " ".join(security_scopes.scopes)
                            ),
                        },
                        403
                    )

            return payload


async def get_current_user(payload: dict = Depends(get_current_token)) -> str:
    return payload["sub"]
