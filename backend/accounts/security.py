from __future__ import annotations
import base64, hashlib, hmac, secrets

class PBKDF2PasswordHasher:
    """Stdlib PBKDF2-HMAC-SHA256 fallback; dependency-free and upgradeable behind a port."""
    algorithm="pbkdf2_sha256"
    iterations=310_000
    def hash(self,password:str)->str:
        if len(password)<8: raise ValueError("password too short")
        salt=secrets.token_bytes(16)
        digest=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,self.iterations)
        return f"{self.algorithm}${self.iterations}${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"
    def verify(self,password:str,encoded:str)->bool:
        try:
            algo,iterations,salt_b64,digest_b64=encoded.split("$",3)
            if algo!=self.algorithm:return False
            salt=base64.urlsafe_b64decode(salt_b64); expected=base64.urlsafe_b64decode(digest_b64)
            actual=hashlib.pbkdf2_hmac("sha256",password.encode(),salt,int(iterations))
            return hmac.compare_digest(actual,expected)
        except Exception:return False

def new_token()->str:return secrets.token_urlsafe(32)
def token_digest(token:str)->str:return hashlib.sha256(token.encode()).hexdigest()
