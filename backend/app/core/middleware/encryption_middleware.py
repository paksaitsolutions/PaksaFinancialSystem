"""
Encryption middleware for automatic data protection.
"""
import json
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.security.encryption import get_encryption_service


class EncryptionMiddleware(BaseHTTPMiddleware):
    """Middleware to automatically encrypt/decrypt sensitive data in requests/responses."""
    
    def __init__(self, app, sensitive_fields: list = None):
        super().__init__(app)
        self.sensitive_fields = sensitive_fields or [
            'ssn', 'social_security_number', 'phone_number', 'bank_account',
            'routing_number', 'tax_id', 'credit_card', 'password'
        ]
        self.encryption_service = get_encryption_service()
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and response for encryption/decryption."""
        # Process request body for encryption
        if request.method in ["POST", "PUT", "PATCH"]:
            request = await self._process_request(request)
        
        # Process the request
        response = await call_next(request)
        
        # Process response for decryption (if needed)
        # Note: This is typically handled by the encrypted field types
        # but could be used for additional processing
        
        return response
    
    async def _process_request(self, request: Request) -> Request:
        """Process request body to encrypt sensitive fields."""
        try:
            # Only process JSON requests
            content_type = request.headers.get("content-type", "")
            if not content_type.startswith("application/json"):
                return request
            
            # Read request body
            body = await request.body()
            if not body:
                return request
            
            # Parse JSON
            try:
                data = json.loads(body)
            except json.JSONDecodeError:
                return request
            
            # Encrypt sensitive fields
            encrypted_data = self._encrypt_sensitive_fields(data)
            
            # Create new request with encrypted data
            if encrypted_data != data:
                new_body = json.dumps(encrypted_data).encode()
                
                # Create a new request with the encrypted body
                async def receive():
                    return {"type": "http.request", "body": new_body}
                
                request._receive = receive
            
        except Exception:
            # If anything goes wrong, return original request
            pass
        
        return request
    
    def _encrypt_sensitive_fields(self, data):
        """Recursively encrypt sensitive fields in data structure."""
        if isinstance(data, dict):
            encrypted_data = {}
            for key, value in data.items():
                if key.lower() in self.sensitive_fields and isinstance(value, str) and value:
                    # Only encrypt if not already encrypted
                    if not self._is_encrypted(value):
                        encrypted_data[key] = self.encryption_service.encrypt(value)
                    else:
                        encrypted_data[key] = value
                elif isinstance(value, (dict, list)):
                    encrypted_data[key] = self._encrypt_sensitive_fields(value)
                else:
                    encrypted_data[key] = value
            return encrypted_data
        elif isinstance(data, list):
            return [self._encrypt_sensitive_fields(item) for item in data]
        else:
            return data
    
    def _is_encrypted(self, value: str) -> bool:
        """Check if a value appears to be encrypted."""
        try:
            self.encryption_service.decrypt(value)
            return True
        except:
            return False