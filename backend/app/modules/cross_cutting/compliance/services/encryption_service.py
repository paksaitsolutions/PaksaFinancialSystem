"""
Paksa Financial System - Encryption Service
Version: 1.0.0
Copyright (c) 2025 Paksa IT Solutions. All rights reserved.

This software is the proprietary information of Paksa IT Solutions.
Use is subject to license terms and restrictions.

Service for handling encryption and decryption of sensitive data.
"""

import base64
import hashlib
import os
from typing import Optional, Union, Dict, Any, Tuple
from uuid import UUID

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

from app.core.config import settings
from .. import exceptions


class EncryptionService:
    """
    Service for handling encryption and decryption of sensitive data.
    
    This service provides methods for symmetric and asymmetric encryption,
    key derivation, and secure hashing.
    """
    
    def __init__(self):
        # Initialize with default encryption key from settings
        self.encryption_key = settings.ENCRYPTION_KEY.encode()
        
        # Ensure the encryption key is the correct length (32 bytes for AES-256)
        if len(self.encryption_key) != 32:
            # Derive a 32-byte key from the provided key using PBKDF2
            salt = b'paksa_financial_system_salt'  # Should be unique per application
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            self.encryption_key = kdf.derive(self.encryption_key)
    
    def generate_key(self) -> bytes:
        """
        Generate a new encryption key.
        
        Returns:
            A new 32-byte encryption key
        """
        return os.urandom(32)
    
    def encrypt_data(
        self,
        data: Union[str, bytes],
        key: Optional[bytes] = None,
        algorithm: str = 'aes-256-cbc'
    ) -> Dict[str, Any]:
        """
        Encrypt data using the specified algorithm.
        
        Args:
            data: The data to encrypt (string or bytes)
            key: Optional encryption key (defaults to instance key)
            algorithm: Encryption algorithm to use ('aes-256-cbc' or 'fernet')
            
        Returns:
            A dictionary containing the encrypted data and any additional parameters
            
        Raises:
            EncryptionError: If encryption fails
        """
        if not data:
            raise exceptions.EncryptionError("No data provided for encryption")
        
        # Convert string data to bytes if needed
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        # Use provided key or instance key
        key = key or self.encryption_key
        
        try:
            if algorithm.lower() == 'fernet':
                # Generate a Fernet key from our encryption key (Fernet requires 32 bytes, URL-safe base64-encoded)
                fernet_key = base64.urlsafe_b64encode(key[:32].ljust(32, b'\0'))
                f = Fernet(fernet_key)
                encrypted = f.encrypt(data)
                return {
                    'encrypted_data': encrypted,
                    'algorithm': 'fernet',
                    'key_id': None
                }
            
            elif algorithm.lower() == 'aes-256-cbc':
                # Generate a random 16-byte IV
                iv = os.urandom(16)
                
                # Create a cipher object with the key and IV
                cipher = Cipher(
                    algorithms.AES(key),
                    modes.CBC(iv),
                    backend=default_backend()
                )
                
                # Pad the data to be a multiple of the block size
                padder = padding.PKCS7(128).padder()
                padded_data = padder.update(data) + padder.finalize()
                
                # Encrypt the data
                encryptor = cipher.encryptor()
                encrypted = encryptor.update(padded_data) + encryptor.finalize()
                
                # Return the encrypted data along with the IV
                return {
                    'encrypted_data': encrypted,
                    'iv': iv,
                    'algorithm': 'aes-256-cbc',
                    'key_id': None
                }
            
            else:
                raise exceptions.EncryptionError(f"Unsupported encryption algorithm: {algorithm}")
                
        except Exception as e:
            raise exceptions.EncryptionError(f"Encryption failed: {str(e)}")
    
    def decrypt_data(
        self,
        encrypted_data: bytes,
        key: Optional[bytes] = None,
        algorithm: str = 'aes-256-cbc',
        iv: Optional[bytes] = None,
        **kwargs
    ) -> bytes:
        """
        Decrypt data using the specified algorithm.
        
        Args:
            encrypted_data: The encrypted data
            key: Optional decryption key (defaults to instance key)
            algorithm: Encryption algorithm used ('aes-256-cbc' or 'fernet')
            iv: Initialization vector (required for AES-CBC)
            **kwargs: Additional algorithm-specific parameters
            
        Returns:
            The decrypted data as bytes
            
        Raises:
            DecryptionError: If decryption fails
        """
        if not encrypted_data:
            raise exceptions.DecryptionError("No encrypted data provided")
        
        # Use provided key or instance key
        key = key or self.encryption_key
        
        try:
            if algorithm.lower() == 'fernet':
                # Generate a Fernet key from our encryption key
                fernet_key = base64.urlsafe_b64encode(key[:32].ljust(32, b'\0'))
                f = Fernet(fernet_key)
                return f.decrypt(encrypted_data)
            
            elif algorithm.lower() == 'aes-256-cbc':
                if not iv:
                    raise exceptions.DecryptionError("IV is required for AES-CBC decryption")
                
                # Create a cipher object with the key and IV
                cipher = Cipher(
                    algorithms.AES(key),
                    modes.CBC(iv),
                    backend=default_backend()
                )
                
                # Decrypt the data
                decryptor = cipher.decryptor()
                padded_data = decryptor.update(encrypted_data) + decryptor.finalize()
                
                # Unpad the data
                unpadder = padding.PKCS7(128).unpadder()
                return unpadder.update(padded_data) + unpadder.finalize()
            
            else:
                raise exceptions.DecryptionError(f"Unsupported decryption algorithm: {algorithm}")
                
        except InvalidToken:
            raise exceptions.DecryptionError("Invalid or corrupted data")
        except Exception as e:
            raise exceptions.DecryptionError(f"Decryption failed: {str(e)}")
    
    def hash_data(
        self,
        data: Union[str, bytes],
        algorithm: str = 'sha256',
        salt: Optional[bytes] = None,
        iterations: int = 100000,
        key_length: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Hash data using the specified algorithm.
        
        Args:
            data: The data to hash (string or bytes)
            algorithm: Hashing algorithm to use ('sha256', 'sha512', 'pbkdf2', 'hmac')
            salt: Optional salt for the hash
            iterations: Number of iterations (for PBKDF2)
            key_length: Length of the derived key (for PBKDF2)
            
        Returns:
            A dictionary containing the hash and any additional parameters
            
        Raises:
            HashingError: If hashing fails
        """
        if not data:
            raise exceptions.HashingError("No data provided for hashing")
        
        # Convert string data to bytes if needed
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        try:
            if algorithm.lower() == 'sha256':
                hash_obj = hashlib.sha256()
                hash_obj.update(data)
                if salt:
                    hash_obj.update(salt)
                return {
                    'hash': hash_obj.digest(),
                    'algorithm': 'sha256',
                    'salt': salt
                }
                
            elif algorithm.lower() == 'sha512':
                hash_obj = hashlib.sha512()
                hash_obj.update(data)
                if salt:
                    hash_obj.update(salt)
                return {
                    'hash': hash_obj.digest(),
                    'algorithm': 'sha512',
                    'salt': salt
                }
                
            elif algorithm.lower() == 'pbkdf2':
                if not salt:
                    salt = os.urandom(16)
                
                if not key_length:
                    key_length = 32  # Default to 32 bytes (256 bits)
                
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=key_length,
                    salt=salt,
                    iterations=iterations,
                    backend=default_backend()
                )
                
                return {
                    'hash': kdf.derive(data),
                    'algorithm': 'pbkdf2',
                    'salt': salt,
                    'iterations': iterations,
                    'key_length': key_length
                }
                
            elif algorithm.lower() == 'hmac':
                if not salt:
                    raise exceptions.HashingError("HMAC requires a key (salt)")
                
                h = hmac.HMAC(
                    salt,
                    hashes.SHA256(),
                    backend=default_backend()
                )
                h.update(data)
                
                return {
                    'hash': h.finalize(),
                    'algorithm': 'hmac-sha256',
                    'key': salt
                }
                
            else:
                raise exceptions.HashingError(f"Unsupported hashing algorithm: {algorithm}")
                
        except Exception as e:
            raise exceptions.HashingError(f"Hashing failed: {str(e)}")
    
    def verify_hash(
        self,
        data: Union[str, bytes],
        hash_data: Dict[str, Any]
    ) -> bool:
        """
        Verify data against a hash.
        
        Args:
            data: The data to verify (string or bytes)
            hash_data: A dictionary containing the hash and algorithm parameters
            
        Returns:
            True if the hash matches, False otherwise
            
        Raises:
            HashingError: If verification fails
        """
        if not data or not hash_data or 'hash' not in hash_data:
            return False
        
        algorithm = hash_data.get('algorithm', 'sha256').lower()
        
        try:
            if algorithm in ['sha256', 'sha512']:
                # For simple hashes, just hash the data with the same parameters and compare
                new_hash = self.hash_data(
                    data,
                    algorithm=algorithm,
                    salt=hash_data.get('salt')
                )
                return hash_data['hash'] == new_hash['hash']
                
            elif algorithm == 'pbkdf2':
                # For PBKDF2, we need all the same parameters
                new_hash = self.hash_data(
                    data,
                    algorithm='pbkdf2',
                    salt=hash_data.get('salt'),
                    iterations=hash_data.get('iterations', 100000),
                    key_length=hash_data.get('key_length', 32)
                )
                return hash_data['hash'] == new_hash['hash']
                
            elif algorithm == 'hmac-sha256':
                # For HMAC, we need the same key
                if 'key' not in hash_data:
                    return False
                    
                new_hash = self.hash_data(
                    data,
                    algorithm='hmac',
                    salt=hash_data['key']
                )
                return hash_data['hash'] == new_hash['hash']
                
            else:
                raise exceptions.HashingError(f"Unsupported hash algorithm for verification: {algorithm}")
                
        except Exception as e:
            raise exceptions.HashingError(f"Hash verification failed: {str(e)}")
    
    def encrypt_field(
        self,
        field_value: Any,
        field_type: str = 'string',
        key_id: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Encrypt a field value with type-specific handling.
        
        Args:
            field_value: The value to encrypt
            field_type: The type of the field ('string', 'number', 'date', 'boolean', 'json')
            key_id: Optional key ID for key management
            **kwargs: Additional encryption parameters
            
        Returns:
            A dictionary containing the encrypted value and metadata
            
        Raises:
            EncryptionError: If encryption fails
        """
        if field_value is None:
            return {
                'encrypted': False,
                'value': None,
                'type': field_type,
                'key_id': key_id
            }
        
        try:
            # Convert the value to a string representation based on type
            if field_type == 'string':
                value_str = str(field_value) if field_value is not None else ''
            elif field_type == 'number':
                value_str = str(field_value) if field_value is not None else '0'
            elif field_type == 'date':
                value_str = field_value.isoformat() if hasattr(field_value, 'isoformat') else str(field_value)
            elif field_type == 'boolean':
                value_str = 'true' if field_value else 'false'
            elif field_type == 'json':
                import json
                value_str = json.dumps(field_value) if field_value else '{}'
            else:
                value_str = str(field_value)
            
            # Encrypt the string representation
            encrypted = self.encrypt_data(
                value_str,
                algorithm=kwargs.get('algorithm', 'aes-256-cbc')
            )
            
            # Return the encrypted data with metadata
            return {
                'encrypted': True,
                'value': base64.b64encode(encrypted['encrypted_data']).decode('utf-8'),
                'iv': base64.b64encode(encrypted['iv']).decode('utf-8') if 'iv' in encrypted else None,
                'algorithm': encrypted['algorithm'],
                'type': field_type,
                'key_id': key_id
            }
            
        except Exception as e:
            raise exceptions.EncryptionError(f"Failed to encrypt field: {str(e)}")
    
    def decrypt_field(
        self,
        encrypted_data: Dict[str, Any],
        **kwargs
    ) -> Any:
        """
        Decrypt a field value with type-specific handling.
        
        Args:
            encrypted_data: A dictionary containing the encrypted value and metadata
            **kwargs: Additional decryption parameters
            
        Returns:
            The decrypted value in its original type
            
        Raises:
            DecryptionError: If decryption fails
        """
        if not encrypted_data or 'encrypted' not in encrypted_data:
            return encrypted_data
        
        if not encrypted_data['encrypted']:
            return encrypted_data.get('value')
        
        try:
            # Extract the encrypted data and IV
            encrypted_value = base64.b64decode(encrypted_data['value'])
            iv = base64.b64decode(encrypted_data['iv']) if 'iv' in encrypted_data and encrypted_data['iv'] else None
            algorithm = encrypted_data.get('algorithm', 'aes-256-cbc')
            field_type = encrypted_data.get('type', 'string')
            
            # Decrypt the data
            decrypted = self.decrypt_data(
                encrypted_value,
                algorithm=algorithm,
                iv=iv,
                **kwargs
            )
            
            # Convert back to the original type
            decrypted_str = decrypted.decode('utf-8')
            
            if field_type == 'string':
                return decrypted_str
            elif field_type == 'number':
                try:
                    return float(decrypted_str) if '.' in decrypted_str else int(decrypted_str)
                except (ValueError, TypeError):
                    return 0
            elif field_type == 'date':
                from datetime import datetime
                try:
                    return datetime.fromisoformat(decrypted_str)
                except (ValueError, TypeError):
                    return None
            elif field_type == 'boolean':
                return decrypted_str.lower() in ('true', '1', 'yes', 'y', 't')
            elif field_type == 'json':
                import json
                try:
                    return json.loads(decrypted_str) if decrypted_str else {}
                except (json.JSONDecodeError, TypeError):
                    return {}
            else:
                return decrypted_str
                
        except Exception as e:
            raise exceptions.DecryptionError(f"Failed to decrypt field: {str(e)}")
    
    def generate_secure_random(
        self,
        length: int = 32,
        encoding: str = 'hex'
    ) -> Union[str, bytes]:
        """
        Generate a secure random string or bytes.
        
        Args:
            length: Length of the random data in bytes
            encoding: Output encoding ('hex', 'base64', 'base64url', 'bytes')
            
        Returns:
            The random data in the specified encoding
            
        Raises:
            ValueError: If an invalid encoding is specified
        """
        if length < 1:
            raise ValueError("Length must be at least 1")
        
        random_bytes = os.urandom(length)
        
        if encoding == 'hex':
            return random_bytes.hex()
        elif encoding == 'base64':
            return base64.b64encode(random_bytes).decode('utf-8')
        elif encoding == 'base64url':
            return base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')
        elif encoding == 'bytes':
            return random_bytes
        else:
            raise ValueError(f"Unsupported encoding: {encoding}")
    
    def generate_key_pair(self, key_size: int = 2048):
        """
        Generate an RSA key pair.
        
        Args:
            key_size: Size of the key in bits (2048 or 4096 recommended)
            
        Returns:
            A tuple containing (private_key, public_key) as PEM-encoded strings
            
        Raises:
            ValueError: If an invalid key size is specified
        """
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.hazmat.primitives import serialization
        
        if key_size not in [1024, 2048, 3072, 4096]:
            raise ValueError("Key size must be 1024, 2048, 3072, or 4096 bits")
        
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size,
            backend=default_backend()
        )
        
        # Get public key
        public_key = private_key.public_key()
        
        # Serialize private key
        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )
        
        # Serialize public key
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        
        return private_pem.decode('utf-8'), public_pem.decode('utf-8')
    
    def sign_data(
        self,
        data: Union[str, bytes],
        private_key: Union[str, bytes],
        algorithm: str = 'sha256'
    ) -> bytes:
        """
        Sign data using a private key.
        
        Args:
            data: The data to sign
            private_key: The private key as a PEM-encoded string or bytes
            algorithm: The hashing algorithm to use ('sha256', 'sha384', 'sha512')
            
        Returns:
            The signature as bytes
            
        Raises:
            SigningError: If signing fails
        """
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if isinstance(private_key, str):
            private_key = private_key.encode('utf-8')
        
        try:
            # Load the private key
            key = serialization.load_pem_private_key(
                private_key,
                password=None,
                backend=default_backend()
            )
            
            # Select the hash algorithm
            if algorithm.lower() == 'sha256':
                hash_alg = hashes.SHA256()
            elif algorithm.lower() == 'sha384':
                hash_alg = hashes.SHA384()
            elif algorithm.lower() == 'sha512':
                hash_alg = hashes.SHA512()
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
            # Sign the data
            signature = key.sign(
                data,
                asym_padding.PSS(
                    mgf=asym_padding.MGF1(hash_alg),
                    salt_length=asym_padding.PSS.MAX_LENGTH
                ),
                hash_alg
            )
            
            return signature
            
        except Exception as e:
            raise exceptions.SigningError(f"Failed to sign data: {str(e)}")
    
    def verify_signature(
        self,
        data: Union[str, bytes],
        signature: bytes,
        public_key: Union[str, bytes],
        algorithm: str = 'sha256'
    ) -> bool:
        """
        Verify a signature using a public key.
        
        Args:
            data: The original data that was signed
            signature: The signature to verify
            public_key: The public key as a PEM-encoded string or bytes
            algorithm: The hashing algorithm used for signing
            
        Returns:
            True if the signature is valid, False otherwise
            
        Raises:
            VerificationError: If verification fails
        """
        from cryptography.hazmat.primitives import hashes
        from cryptography.hazmat.primitives.asymmetric import padding as asym_padding
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        from cryptography.exceptions import InvalidSignature
        
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        if isinstance(public_key, str):
            public_key = public_key.encode('utf-8')
        
        try:
            # Load the public key
            key = serialization.load_pem_public_key(
                public_key,
                backend=default_backend()
            )
            
            # Select the hash algorithm
            if algorithm.lower() == 'sha256':
                hash_alg = hashes.SHA256()
            elif algorithm.lower() == 'sha384':
                hash_alg = hashes.SHA384()
            elif algorithm.lower() == 'sha512':
                hash_alg = hashes.SHA512()
            else:
                raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
            # Verify the signature
            try:
                key.verify(
                    signature,
                    data,
                    asym_padding.PSS(
                        mgf=asym_padding.MGF1(hash_alg),
                        salt_length=asym_padding.PSS.MAX_LENGTH
                    ),
                    hash_alg
                )
                return True
            except InvalidSignature:
                return False
                
        except Exception as e:
            raise exceptions.VerificationError(f"Signature verification failed: {str(e)}")
