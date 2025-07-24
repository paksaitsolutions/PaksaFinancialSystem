import re

class PasswordPolicy:
    MIN_LENGTH = 8
    REQUIRE_UPPER = True
    REQUIRE_LOWER = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = r"!@#$%^&*()_+-=[]{}|;:',.<>/?"

    @classmethod
    def validate(cls, password: str) -> bool:
        if len(password) < cls.MIN_LENGTH:
            return False
        if cls.REQUIRE_UPPER and not re.search(r'[A-Z]', password):
            return False
        if cls.REQUIRE_LOWER and not re.search(r'[a-z]', password):
            return False
        if cls.REQUIRE_DIGIT and not re.search(r'[0-9]', password):
            return False
        if cls.REQUIRE_SPECIAL and not re.search(r'[' + re.escape(cls.SPECIAL_CHARS) + ']', password):
            return False
        return True

    @classmethod
    def get_policy_description(cls) -> str:
        return (
            f"Password must be at least {cls.MIN_LENGTH} characters, "
            f"contain upper and lower case letters, a digit, and a special character."
        )
