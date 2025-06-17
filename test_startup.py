#!/usr/bin/env python3
"""Test script to verify the application can start properly."""
import os
import sys

# Set minimal environment variables for testing
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("KLING_ACCESS_KEY", "test-key")
os.environ.setdefault("KLING_SECRET_KEY", "test-key")

try:
    # Test imports
    print("Testing imports...")
    from app.main import app
    print("✓ Main app imported successfully")
    
    from app.core.config import settings
    print("✓ Settings loaded successfully")
    print(f"  - Project: {settings.PROJECT_NAME}")
    print(f"  - Version: {settings.VERSION}")
    print(f"  - Database URL: {settings.DATABASE_URL[:30]}...")
    
    # Test database models
    from app.models import *
    print("✓ Models imported successfully")
    
    # Test API endpoints
    from app.api.v1.api import api_router
    print("✓ API router imported successfully")
    
    print("\n✅ All imports successful! The application should start properly.")
    
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)