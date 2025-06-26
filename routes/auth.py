from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()
router = APIRouter()

JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret_fallback")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

MOCK_USER = {
    "email": "test@example.com",
    "username": "testuser",
    "hashed_password": pwd_context.hash("testpass")
}

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str  # This will actually contain the email
    password: str

class Token(BaseModel):
    token: str
    token_type: str

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=ALGORITHM)

@router.post("/register", response_model=Token)
async def register(user: UserCreate):
    # For mock system, only check email
    if user.email == MOCK_USER["email"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Generate username from email if not provided
    username = user.username or user.email.split('@')[0]
    
    # Create token with both email and username
    token = create_access_token({
        "sub": user.email,
        "username": username
    })
    
    return {"token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(form_data: LoginRequest):
    # Check if the provided username (email) and password match the mock user
    if form_data.username != MOCK_USER["email"] or not verify_password(form_data.password, MOCK_USER["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Create token with both email and username
    token = create_access_token({
        "sub": MOCK_USER["email"],
        "username": MOCK_USER["username"]
    })
    
    return {"token": token, "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.get("/me")
async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[ALGORITHM])
        email = payload.get("sub")
        username = payload.get("username")
        
        if email is None or email != MOCK_USER["email"]:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
            
        return {
            "username": username or MOCK_USER["username"],
            "email": email
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )