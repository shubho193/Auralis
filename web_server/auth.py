from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from hashlib import sha256
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, database

# Secret key for JWT encoding/decoding. 
# IN PRODUCTION, CHANGE THIS TO A STRONG RANDOM SECRET!
SECRET_KEY = "supersecretkey" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 4320 # 3 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_password(plain_password, hashed_password):
    # Hash the plain password with SHA256 first to avoid bcrypt 72 byte limit
    pre_hashed = sha256(plain_password.encode('utf-8')).hexdigest()
    return pwd_context.verify(pre_hashed, hashed_password)

def get_password_hash(password):
    # Hash the password with SHA256 first
    pre_hashed = sha256(password.encode('utf-8')).hexdigest()
    return pwd_context.hash(pre_hashed)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user
