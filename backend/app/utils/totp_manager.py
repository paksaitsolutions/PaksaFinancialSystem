import pyotp

class TOTPManager:
    @staticmethod
    def generate_secret():
        return pyotp.random_base32()

    @staticmethod
    def get_uri(secret, email, issuer_name="PaksaFinancialSystem"):
        return pyotp.totp.TOTP(secret).provisioning_uri(name=email, issuer_name=issuer_name)

    @staticmethod
    def verify_code(secret, code):
        totp = pyotp.TOTP(secret)
        return totp.verify(code)
