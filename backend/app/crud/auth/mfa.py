"""
MFA CRUD operations.
"""
import secrets
import hashlib
import hmac
import struct
import time
import base64
import json
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.auth.mfa import MFADevice, MFAAttempt
from app.schemas.auth.mfa import MFADeviceCreate, MFASetupResponse

class MFACRUD:
    """MFA CRUD operations."""
    
    async def create_device(
        self, 
        db: AsyncSession, 
        *, 
        user_id: UUID, 
        device_data: MFADeviceCreate
    ) -> MFADevice:
        """Create MFA device."""
        secret_key = None
        if device_data.device_type == "totp":
            secret_key = base64.b32encode(secrets.token_bytes(20)).decode().rstrip('=')
        
        # Generate backup codes
        backup_codes = [secrets.token_hex(4).upper() for _ in range(10)]
        
        device = MFADevice(
            user_id=user_id,
            device_name=device_data.device_name,
            device_type=device_data.device_type,
            secret_key=secret_key,
            phone_number=device_data.phone_number,
            email=device_data.email,
            backup_codes=json.dumps(backup_codes)
        )
        
        db.add(device)
        await db.commit()
        await db.refresh(device)
        return device
    
    async def get_user_devices(self, db: AsyncSession, user_id: UUID) -> List[MFADevice]:
        """Get user's MFA devices."""
        query = select(MFADevice).where(
            and_(MFADevice.user_id == user_id, MFADevice.is_active == True)
        )
        result = await db.execute(query)
        return result.scalars().all()
    
    async def get_device(self, db: AsyncSession, device_id: UUID) -> Optional[MFADevice]:
        """Get MFA device by ID."""
        query = select(MFADevice).where(MFADevice.id == device_id)
        result = await db.execute(query)
        return result.scalars().first()
    
    async def verify_device(self, db: AsyncSession, device_id: UUID) -> bool:
        """Mark device as verified."""
        device = await self.get_device(db, device_id)
        if device:
            device.is_verified = True
            await db.commit()
            return True
        return False
    
    async def verify_totp_code(self, device: MFADevice, code: str) -> bool:
        """Verify TOTP code."""
        if device.device_type != "totp" or not device.secret_key:
            return False
        
        return self._verify_totp(device.secret_key, code)
    
    async def verify_backup_code(self, db: AsyncSession, device: MFADevice, code: str) -> bool:
        """Verify backup code."""
        if not device.backup_codes:
            return False
        
        backup_codes = json.loads(device.backup_codes)
        if code.upper() in backup_codes:
            # Remove used backup code
            backup_codes.remove(code.upper())
            device.backup_codes = json.dumps(backup_codes)
            await db.commit()
            return True
        return False
    
    async def log_attempt(
        self, 
        db: AsyncSession, 
        *, 
        user_id: UUID, 
        device_id: UUID, 
        attempt_type: str, 
        code: str, 
        success: bool, 
        ip_address: str = None
    ):
        """Log MFA attempt."""
        attempt = MFAAttempt(
            user_id=user_id,
            device_id=device_id,
            attempt_type=attempt_type,
            code_used=code[:3] + "***",  # Partial code for security
            is_successful=success,
            ip_address=ip_address
        )
        db.add(attempt)
        await db.commit()
    
    async def generate_qr_code(self, device: MFADevice, user_email: str) -> str:
        """Generate QR code for TOTP setup."""
        if device.device_type != "totp" or not device.secret_key:
            return None
        
        provisioning_uri = f"otpauth://totp/Paksa Financial System:{user_email}?secret={device.secret_key}&issuer=Paksa Financial System"
        return provisioning_uri
    
    async def disable_device(self, db: AsyncSession, device_id: UUID) -> bool:
        """Disable MFA device."""
        device = await self.get_device(db, device_id)
        if device:
            device.is_active = False
            await db.commit()
            return True
        return False

    def _verify_totp(self, secret: str, token: str) -> bool:
        """Simple TOTP verification."""
        try:
            secret = secret.upper()
            missing_padding = len(secret) % 8
            if missing_padding:
                secret += '=' * (8 - missing_padding)
            
            key = base64.b32decode(secret)
            current_time = int(time.time()) // 30
            
            for time_window in [current_time - 1, current_time, current_time + 1]:
                expected = self._generate_totp(key, time_window)
                if expected == token:
                    return True
            return False
        except:
            return False
    
    def _generate_totp(self, key: bytes, time_counter: int) -> str:
        """Generate TOTP token."""
        time_bytes = struct.pack('>Q', time_counter)
        hmac_hash = hmac.new(key, time_bytes, hashlib.sha1).digest()
        offset = hmac_hash[-1] & 0x0f
        truncated = struct.unpack('>I', hmac_hash[offset:offset + 4])[0] & 0x7fffffff
        return str(truncated % 1000000).zfill(6)

# Create instance
mfa_crud = MFACRUD()