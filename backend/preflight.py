#!/usr/bin/env python3
"""
Pre-flight check script for τέλειος backend.
Verifies environment is ready before starting the server.

Usage:
    python preflight.py
"""
import sys
import os
from pathlib import Path
import json

def check_python_version():
    """Check Python version is 3.10+."""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 10):
        print("   ❌ Python 3.10+ required")
        return False
    print("   ✅ Python version OK")
    return True


def check_dependencies():
    """Check critical dependencies are installed."""
    required = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "httpx",
        "structlog",
        "pydantic",
    ]
    
    optional = [
        ("chromadb", "Vector store (can use in-memory fallback)"),
        ("pymupdf", "PDF parsing (OCR functionality)"),
        ("RestrictedPython", "Code sandbox (execution functionality)"),
        ("easyocr", "OCR engine (optional, can use pytesseract)"),
    ]
    
    missing_required = []
    missing_optional = []
    
    print("Checking required dependencies...")
    for package in required:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} NOT FOUND")
            missing_required.append(package)
    
    print("\nChecking optional dependencies...")
    for package, purpose in optional:
        try:
            __import__(package)
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ⚠️  {package} not installed ({purpose})")
            missing_optional.append((package, purpose))
    
    if missing_required:
        print(f"\n❌ Missing required packages: {', '.join(missing_required)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    if missing_optional:
        print(f"\n⚠️  {len(missing_optional)} optional package(s) missing")
        print("Some features may be limited. Install with:")
        for pkg, _ in missing_optional:
            print(f"   pip install {pkg}")
    
    return True


def check_config_files():
    """Check all config files exist and are valid."""
    config_dir = Path(__file__).parent.parent / "config"
    
    required_configs = [
        "app.json",
        "models.json",
        "agents.json",
        "gateway.json",
        "tools.json",
    ]
    
    print(f"\nChecking config files in {config_dir}...")
    
    all_valid = True
    for config_file in required_configs:
        config_path = config_dir / config_file
        
        if not config_path.exists():
            print(f"   ❌ {config_file} not found")
            all_valid = False
            continue
        
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                json.load(f)
            print(f"   ✅ {config_file}")
        except json.JSONDecodeError as e:
            print(f"   ❌ {config_file} invalid JSON: {e}")
            all_valid = False
    
    return all_valid


def check_directory_structure():
    """Check required directories exist."""
    backend_dir = Path(__file__).parent
    
    required_dirs = [
        "db",
        "services",
        "adapters",
        "agents",
        "tools",
        "gateway",
    ]
    
    print("\nChecking directory structure...")
    
    all_exist = True
    for dir_name in required_dirs:
        dir_path = backend_dir / dir_name
        if dir_path.exists() and dir_path.is_dir():
            print(f"   ✅ {dir_name}/")
        else:
            print(f"   ❌ {dir_name}/ not found")
            all_exist = False
    
    return all_exist


def check_data_directory():
    """Check/create data directory."""
    data_dir = Path(__file__).parent.parent / "data"
    uploads_dir = data_dir / "uploads"
    
    print("\nChecking data directories...")
    
    if not data_dir.exists():
        print(f"   ⚠️  Creating {data_dir}")
        data_dir.mkdir(parents=True, exist_ok=True)
    else:
        print(f"   ✅ {data_dir}")
    
    if not uploads_dir.exists():
        print(f"   ⚠️  Creating {uploads_dir}")
        uploads_dir.mkdir(parents=True, exist_ok=True)
    else:
        print(f"   ✅ {uploads_dir}")
    
    return True


def check_env_variables():
    """Check environment variables."""
    print("\nChecking environment variables...")
    
    important_vars = {
        "DB_URL": "Database connection string",
        "OLLAMA_BASE_URL": "Ollama API endpoint",
        "OPENAI_API_KEY": "OpenAI API key (if using OpenAI)",
        "ANTHROPIC_API_KEY": "Anthropic API key (if using Anthropic)",
    }
    
    any_set = False
    for var, description in important_vars.items():
        if os.environ.get(var):
            print(f"   ✅ {var} set")
            any_set = True
        else:
            print(f"   ℹ️  {var} not set ({description})")
    
    if not any_set:
        print("\n   ℹ️  No environment variables set - using config file defaults")
    
    return True  # Not critical


def main():
    """Run all pre-flight checks."""
    print("="*60)
    print("τέλειος Backend Pre-flight Check")
    print("="*60 + "\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Config Files", check_config_files),
        ("Directory Structure", check_directory_structure),
        ("Data Directories", check_data_directory),
        ("Environment Variables", check_env_variables),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"\n❌ {check_name} check crashed: {e}")
            results.append((check_name, False))
    
    # Summary
    print("\n" + "="*60)
    print("PRE-FLIGHT SUMMARY")
    print("="*60 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status} - {check_name}")
    
    print(f"\n{'='*60}")
    
    if passed == total:
        print("✅ ALL CHECKS PASSED!")
        print("\nYou can now start the server:")
        print("  uvicorn main:app --reload --host 0.0.0.0 --port 8005")
        return 0
    else:
        print(f"⚠️  {total - passed} CHECK(S) FAILED")
        print("\nFix the issues above before starting the server.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
