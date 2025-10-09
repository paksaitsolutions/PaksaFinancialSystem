import re

# Read the main.py file
with open('d:/PaksaFinancialSystem/backend/app/main.py', 'r') as f:
    content = f.read()

# Replace all occurrences of user["tenant_id"] with user.get("tenant_id", DEFAULT_TENANT_ID)
content = content.replace('user["tenant_id"]', 'user.get("tenant_id", DEFAULT_TENANT_ID)')

# Write back to the file
with open('d:/PaksaFinancialSystem/backend/app/main.py', 'w') as f:
    f.write(content)

print("Fixed all tenant_id KeyError occurrences")