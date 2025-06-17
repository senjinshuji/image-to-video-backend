#!/usr/bin/env python3
"""Debug environment variables during deployment"""

import os
import sys

print("=== Environment Variables Debug ===")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")
print()

# Check for required environment variables
required_vars = [
    "DATABASE_URL",
    "OPENAI_API_KEY", 
    "KLING_ACCESS_KEY",
    "KLING_SECRET_KEY",
    "JWT_SECRET_KEY",
    "BACKEND_CORS_ORIGINS",
    "APP_ENV",
    "DEBUG"
]

print("Environment variables status:")
for var in required_vars:
    value = os.environ.get(var)
    if value:
        # Mask sensitive values
        if "KEY" in var or "SECRET" in var or "DATABASE" in var:
            masked = value[:5] + "..." + value[-5:] if len(value) > 10 else "***"
            print(f"✓ {var}: {masked}")
        else:
            print(f"✓ {var}: {value}")
    else:
        print(f"✗ {var}: NOT SET")

print("\nAll environment variables:")
for key in sorted(os.environ.keys()):
    if any(word in key.upper() for word in ["API", "KEY", "SECRET", "DATABASE", "KLING", "OPENAI", "CORS", "JWT", "APP", "DEBUG"]):
        value = os.environ[key]
        if any(sensitive in key.upper() for sensitive in ["KEY", "SECRET", "PASSWORD", "DATABASE"]):
            masked = value[:5] + "..." + value[-5:] if len(value) > 10 else "***"
            print(f"  {key}: {masked}")
        else:
            print(f"  {key}: {value}")