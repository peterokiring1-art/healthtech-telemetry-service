from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Dict

# Import our updated native cryptography handlers
from security import hash_password, verify_password, create_access_token

router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Security & Authentication"]
)

# In-memory mock database populated safely using native bcrypt
MOCK_USER_DB: Dict[str, str] = {
    "clinician_peter": hash_password("secure_password_2026")
}

class TokenResponse(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=TokenResponse, summary="Authenticate Clinician or Device Node")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user_hash = MOCK_USER_DB.get(form_data.username)
    
    if not user_hash or not verify_password(form_data.password, user_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password combination",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}
