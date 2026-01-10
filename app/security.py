from fastapi import Header, HTTPException
import app.config as config


def verify_internal_token(x_internal_token: str = Header(None)):
    if x_internal_token != config.INTERNAL_SERVICE_TOKEN:
        raise HTTPException(status_code=403, detail="Forbidden")
