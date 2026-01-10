from fastapi import Header, HTTPException
import os

INTERNAL_SERVICE_TOKEN = os.getenv("INTERNAL_SERVICE_TOKEN")

def verify_internal_token(authorization: str = Header(None)):
    if not INTERNAL_SERVICE_TOKEN:
        raise HTTPException(status_code=500, detail="Server misconfigured")

    if not authorization:
        raise HTTPException(status_code=403, detail="Missing auth")

    scheme, _, token = authorization.partition(" ")

    if scheme.lower() != "bearer" or token != INTERNAL_SERVICE_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
