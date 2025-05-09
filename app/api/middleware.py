import requests
from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

class BearerTokenMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, protected_paths: list[str]):
        super().__init__(app)
        self.protected_paths = protected_paths
        self.auth_check_url = "http://user-service/api/check-token"

    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        if path in self.protected_paths:
            auth_header = request.headers.get("Authorization")

            if not auth_header or not auth_header.startswith("Bearer "):
                return JSONResponse({"detail": "Token manquant ou invalide."}, status_code=401)

            token = auth_header.split(" ")[1]

            try:
                response = requests.get(
                    self.auth_check_url,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5
                )

                if response.status_code != 200:
                    return JSONResponse({"detail": "Token invalide."}, status_code=403)

            except requests.RequestException:
                return JSONResponse(
                    {"detail": "Erreur de connexion au service d'authentification."},
                    status_code=500
                )

        return await call_next(request)
