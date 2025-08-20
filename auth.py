from fastapi import HTTPException, Header

def get_current_user(authorization: str = Header(...)):
    # Very simple demo auth: require token 'Bearer demo'
    if authorization != "Bearer demo":
        raise HTTPException(401, "Unauthorized")
    return {"username": "demo_user", "role": "admin"}
