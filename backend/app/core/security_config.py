"""
Paksa Financial System - Security Configuration
Copyright (c) 2024 Paksa IT Solutions
"""

# Code ownership and branding
COMPANY_NAME = "Paksa IT Solutions"
PRODUCT_NAME = "Paksa Financial System"
COPYRIGHT_YEAR = "2024"
COMPANY_WEBSITE = "https://paksa.com"
COMPANY_EMAIL = "info@paksa.com"

# Git repository configuration
GIT_REPO_URL = "https://github.com/paksaitsolutions/paksa-financial-system"
GIT_BRANCH_STRATEGY = {
    "main": "Production-ready code",
    "develop": "Integration branch",
    "feature/*": "Feature development",
    "bugfix/*": "Bug fixes",
    "hotfix/*": "Critical fixes"
}

# Code security settings
ENABLE_CODE_OBFUSCATION = False  # Set to True for production
ENABLE_LICENSE_CHECK = True
REQUIRE_ATTRIBUTION = True

# Watermark settings
CODE_WATERMARK = f"© {COPYRIGHT_YEAR} {COMPANY_NAME} - {PRODUCT_NAME}"
API_RESPONSE_HEADER = {
    "X-Powered-By": PRODUCT_NAME,
    "X-Company": COMPANY_NAME
}

# Development tracking
TRACK_CODE_CHANGES = True
REQUIRE_COMMIT_SIGNATURE = True
ENFORCE_BRANCH_PROTECTION = True