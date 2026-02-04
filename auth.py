import json
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import argon2
from models import User, UserInDB

# Constants
SECRET_KEY = "your-secret-key-here"  # In production, use environment variable
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

hasher = argon2.PasswordHasher()

USERS_FILE = "users.json"

def hash_password(password: str) -> str:
    return hasher.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return hasher.verify(hashed_password, plain_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def generate_reset_token() -> str:
    return secrets.token_urlsafe(32)

def load_users() -> dict:
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users: dict):
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def get_user(email: str) -> Optional[UserInDB]:
    users = load_users()
    if email in users:
        user_data = users[email]
        return UserInDB(**user_data)
    return None

def create_user(email: str, password: str) -> UserInDB:
    hashed_password = hash_password(password)
    user = UserInDB(email=email, hashed_password=hashed_password)
    users = load_users()
    users[email] = user.dict()
    save_users(users)
    return user

def update_user(email: str, **kwargs):
    users = load_users()
    if email in users:
        users[email].update(kwargs)
        save_users(users)

def authenticate_user(email: str, password: str) -> Optional[UserInDB]:
    user = get_user(email)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user
