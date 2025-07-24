from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.models.user import User
from app.models.role import Role
from app.models.permission import UserPermission
from app.models.company import Company
from app.schemas.user_schemas import UserCreate, UserOut
from app.core.security import get_password_hash
from app.db.session import get_db
from app.utils.totp_manager import TOTPManager
from fastapi import Body
from app.models.user import UserLoginHistory, UserActivityLog
from app.utils.password_policy import PasswordPolicy

router = APIRouter(prefix="/users", tags=["User Management"])

@router.post("/invite", response_model=UserOut)
async def invite_user(user_in: UserCreate, company_id: str, db: AsyncSession = Depends(get_db)):
    # Check if company exists
    company = await db.get(Company, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")
    # Check if user already exists
    existing = await User.get_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="User already exists")
    # Enforce password policy
    if not PasswordPolicy.validate(user_in.password):
        raise HTTPException(status_code=400, detail=f"Password does not meet policy: {PasswordPolicy.get_policy_description()}")
    # Create user
    hashed_password = get_password_hash(user_in.password)
    user = User(
        email=user_in.email,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        hashed_password=hashed_password,
        is_active=True,
        company_id=company_id,
        role_id=user_in.role_id
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Actual email invitation logic
    from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
    conf = ConnectionConfig(
        MAIL_USERNAME = "your_email@example.com",
        MAIL_PASSWORD = "your_password",
        MAIL_FROM = "your_email@example.com",
        MAIL_PORT = 587,
        MAIL_SERVER = "smtp.example.com",
        MAIL_TLS = True,
        MAIL_SSL = False,
        USE_CREDENTIALS = True
    )
    message = MessageSchema(
        subject="You're invited to join " + company.name,
        recipients=[user.email],
        body=f"Hello {user.first_name},\nYou have been invited to join {company.name} on Paksa Financial System. Please follow the link to set your password and activate your account.",
        subtype="plain"
    )
    fm = FastMail(conf)
    await fm.send_message(message)
    return user

@router.post("/assign-role", response_model=UserOut)
async def assign_role(user_id: str, role_id: str, company_id: str, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user or user.company_id != company_id:
        raise HTTPException(status_code=404, detail="User not found or not in company")
    role = await db.get(Role, role_id)
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    user.role_id = role_id
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@router.post("/set-permissions", response_model=UserOut)
async def set_permissions(user_id: str, permissions: List[str], company_id: str, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user or user.company_id != company_id:
        raise HTTPException(status_code=404, detail="User not found or not in company")
    # Remove existing permissions
    await db.execute(f"DELETE FROM user_permissions WHERE user_id = '{user_id}'")
    # Add new permissions
    for perm in permissions:
        db.add(UserPermission(user_id=user_id, permission_name=perm))
    await db.commit()
    await db.refresh(user)
    return user

@router.get("/company/{company_id}", response_model=List[UserOut])
async def list_company_users(company_id: str, db: AsyncSession = Depends(get_db)):
    # List all users for a company (isolation enforced)
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.company_id == company_id))
    return result.scalars().all()

# MFA Endpoints
@router.post("/enable-mfa/{user_id}")
async def enable_mfa(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.mfa_enabled:
        raise HTTPException(status_code=400, detail="MFA already enabled")
    secret = TOTPManager.generate_secret()
    user.mfa_secret = secret
    user.mfa_enabled = True
    db.add(user)
    await db.commit()
    await db.refresh(user)
    uri = TOTPManager.get_uri(secret, user.email)
    return {"mfa_enabled": True, "mfa_uri": uri, "mfa_secret": secret}

@router.post("/disable-mfa/{user_id}")
async def disable_mfa(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.mfa_enabled = False
    user.mfa_secret = None
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"mfa_enabled": False}

@router.post("/verify-mfa/{user_id}")
async def verify_mfa(user_id: str, code: str = Body(...), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user or not user.mfa_enabled or not user.mfa_secret:
        raise HTTPException(status_code=404, detail="MFA not enabled for user")
    valid = TOTPManager.verify_code(user.mfa_secret, code)
    if not valid:
        raise HTTPException(status_code=400, detail="Invalid MFA code")
    return {"mfa_verified": True}

# Login history endpoints
@router.post("/login-history/{user_id}")
async def record_login_history(user_id: str, ip_address: str = Body(None), user_agent: str = Body(None), success: bool = Body(True), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    login_event = UserLoginHistory(user_id=user_id, ip_address=ip_address, user_agent=user_agent, success=success)
    db.add(login_event)
    await db.commit()
    return {"login_recorded": True}

@router.get("/login-history/{user_id}")
async def get_login_history(user_id: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(UserLoginHistory).where(UserLoginHistory.user_id == user_id))
    return result.scalars().all()

# User activity log endpoints
@router.post("/activity-log/{user_id}")
async def record_activity_log(user_id: str, activity_type: str = Body(...), description: str = Body(None), ip_address: str = Body(None), user_agent: str = Body(None), db: AsyncSession = Depends(get_db)):
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    log = UserActivityLog(user_id=user_id, activity_type=activity_type, description=description, ip_address=ip_address, user_agent=user_agent)
    db.add(log)
    await db.commit()
    return {"activity_logged": True}

@router.get("/activity-log/{user_id}")
async def get_activity_logs(user_id: str, db: AsyncSession = Depends(get_db)):
    from sqlalchemy import select
    result = await db.execute(select(UserActivityLog).where(UserActivityLog.user_id == user_id))
    return result.scalars().all()

# Password reset endpoints
from app.models.user import PasswordResetToken
import secrets
from datetime import datetime, timedelta

@router.post("/password-reset/request")
async def request_password_reset(email: str = Body(...), db: AsyncSession = Depends(get_db)):
    user = await User.get_by_email(db, email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)
    reset_token = PasswordResetToken(user_id=user.id, token=token, expires_at=expires_at)
    db.add(reset_token)
    await db.commit()
    # Send email logic here (reuse FastMail config)
    # ...
    return {"reset_token": token, "expires_at": expires_at}

@router.post("/password-reset/verify")
async def verify_password_reset_token(token: str = Body(...), db: AsyncSession = Depends(get_db)):
    reset_token = await PasswordResetToken.get_by_token(db, token)
    if not reset_token or reset_token.is_expired or reset_token.used:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    return {"valid": True}

@router.post("/password-reset/set")
async def set_new_password(token: str = Body(...), new_password: str = Body(...), db: AsyncSession = Depends(get_db)):
    reset_token = await PasswordResetToken.get_by_token(db, token)
    if not reset_token or reset_token.is_expired or reset_token.used:
        raise HTTPException(status_code=400, detail="Invalid or expired token")
    user = await db.get(User, reset_token.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not PasswordPolicy.validate(new_password):
        raise HTTPException(status_code=400, detail=f"Password does not meet policy: {PasswordPolicy.get_policy_description()}")
    user.hashed_password = get_password_hash(new_password)
    db.add(user)
    reset_token.used = True
    db.add(reset_token)
    await db.commit()
    return {"password_reset": True}
