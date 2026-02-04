from datetime import timedelta
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from fastapi.staticfiles import StaticFiles
from models import User, UserCreate, UserLogin, Token, ResetPasswordRequest, ResetPasswordConfirm
from auth import authenticate_user, create_access_token, create_user, get_user, update_user, generate_reset_token, verify_password, hash_password
from logger import logger

app = FastAPI(title="FundooNotes API", description="Backend API for FundooNotes app")

# Serve static files from frontend directory
app.mount("/static", StaticFiles(directory="frontend"), name="static")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/register", response_model=User)
async def register(user: UserCreate):
    db_user = get_user(user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    new_user = create_user(user.email, user.password)
    logger.info(f"User registered: {user.email}")
    return User(email=new_user.email)

@app.post("/login", response_model=Token)
async def login(user: UserLogin):
    db_user = authenticate_user(user.email, user.password)
    if not db_user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": db_user.email}, expires_delta=access_token_expires
    )
    logger.info(f"User logged in: {user.email}")
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/reset-password")
async def reset_password(request: ResetPasswordRequest):
    db_user = get_user(request.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="Email not found")
    reset_token = generate_reset_token()
    update_user(request.email, reset_token=reset_token)
    logger.info(f"Password reset requested for: {request.email}")
    # In a real app, send email with token. For now, just return it.
    return {"message": "Reset token generated", "reset_token": reset_token}

@app.post("/reset-password/confirm")
async def reset_password_confirm(request: ResetPasswordConfirm):
    db_user = get_user(request.email)
    if not db_user:
        raise HTTPException(status_code=400, detail="Email not found")
    if db_user.reset_token != request.reset_token:
        raise HTTPException(status_code=400, detail="Invalid reset token")
    # Update password
    from auth import hash_password
    hashed_password = hash_password(request.new_password)
    update_user(request.email, hashed_password=hashed_password, reset_token=None)
    logger.info(f"Password reset confirmed for: {request.email}")
    return {"message": "Password reset successfully"}



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
