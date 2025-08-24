from fastapi import HTTPException, Header
from typing import Optional

def get_current_user(authorization: Optional[str] = Header(None)):
    # Very simple demo auth: allow demo token or no auth for testing
    if authorization and authorization != "Bearer demo":
        raise HTTPException(401, "Unauthorized")
    return {"username": "demo_user", "role": "admin"}
