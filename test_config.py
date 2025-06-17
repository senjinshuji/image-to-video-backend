#!/usr/bin/env python3
"""Test configuration loading without dependencies."""
import os
import sys

# Set minimal environment variables
os.environ.setdefault("DATABASE_URL", "postgresql://user:pass@localhost/db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("KLING_ACCESS_KEY", "test-key")
os.environ.setdefault("KLING_SECRET_KEY", "test-key")
os.environ.setdefault("BACKEND_CORS_ORIGINS", '["http://localhost:3000"]')

try:
    print("Testing configuration loading...")
    
    # Add app directory to path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Test pydantic_settings import
    try:
        from pydantic_settings import BaseSettings
        print("✓ pydantic_settings imported")
    except ImportError:
        print("✗ pydantic_settings not available - need to install requirements")
        sys.exit(1)
    
    # Test config import
    from app.core.config import settings
    print("✓ Settings loaded successfully")
    print(f"  - Project: {settings.PROJECT_NAME}")
    print(f"  - Version: {settings.VERSION}")
    print(f"  - Database URL parsed: {settings.DATABASE_URL[:30]}...")
    print(f"  - CORS Origins: {settings.BACKEND_CORS_ORIGINS}")
    
    print("\n✅ Configuration loads correctly!")
    
except Exception as e:
    print(f"\n❌ Error: {type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)