"""
Test script to verify all config files are valid JSON and contain expected keys.

Usage:
    python test_config.py
"""
import json
import sys
from pathlib import Path

CONFIG_DIR = Path(__file__).parent.parent / "config"

EXPECTED_CONFIGS = {
    "app.json": ["platform", "version", "storage", "ocr", "sandbox", "limits"],
    "models.json": ["active_provider", "providers", "embedding"],
    "agents.json": ["orchestrator", "document", "retrieval", "qa", "explanation", "execution", "prediction"],
    "gateway.json": ["api", "server", "cors", "endpoints"],
    "tools.json": ["tools"],
    "prediction.json": ["weights", "top_n", "min_score_threshold"],
    "server.json": [],  # Can be empty or have server settings
    "adapters.json": [],  # Can be empty or have adapter settings
    "frontend.json": ["app", "server", "api", "ui", "features"],
}

def test_config_files():
    """Test all config files."""
    errors = []
    
    print(f"Testing config files in: {CONFIG_DIR}\n")
    
    for config_file, expected_keys in EXPECTED_CONFIGS.items():
        config_path = CONFIG_DIR / config_file
        
        # Check file exists
        if not config_path.exists():
            errors.append(f"❌ {config_file}: File not found")
            print(errors[-1])
            continue
        
        # Check valid JSON
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"❌ {config_file}: Invalid JSON - {e}")
            print(errors[-1])
            continue
        
        # Check expected keys
        missing_keys = [key for key in expected_keys if key not in config]
        if missing_keys:
            errors.append(f"❌ {config_file}: Missing keys: {missing_keys}")
            print(errors[-1])
        else:
            print(f"✅ {config_file}: Valid ({len(config)} top-level keys)")
    
    # Summary
    print("\n" + "="*60)
    if errors:
        print(f"❌ FAILED: {len(errors)} config error(s) found:\n")
        for error in errors:
            print(error)
        return False
    else:
        print(f"✅ SUCCESS: All {len(EXPECTED_CONFIGS)} config files valid!")
        return True

def print_config_summary():
    """Print summary of all config values (for verification)."""
    print("\n" + "="*60)
    print("Configuration Summary:")
    print("="*60 + "\n")
    
    for config_file in EXPECTED_CONFIGS.keys():
        config_path = CONFIG_DIR / config_file
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = json.load(f)
            
            print(f"📄 {config_file}:")
            if config_file == "app.json":
                print(f"   Platform: {config.get('platform')}")
                print(f"   Version: {config.get('version')}")
                print(f"   DB URL: {config.get('storage', {}).get('db_url')}")
                print(f"   Vector Backend: {config.get('storage', {}).get('vector_backend')}")
            elif config_file == "models.json":
                print(f"   Active Provider: {config.get('active_provider')}")
                providers = config.get('providers', {})
                for provider in providers:
                    provider_cfg = providers[provider]
                    print(f"   {provider}: {provider_cfg.get('base_url') or provider_cfg.get('api_base', 'N/A')}")
            elif config_file == "gateway.json":
                print(f"   API Title: {config.get('api', {}).get('title')}")
                print(f"   Port: {config.get('server', {}).get('port')}")
                print(f"   CORS Origins: {config.get('cors', {}).get('origins')}")
            elif config_file == "agents.json":
                print(f"   Orchestrator Timeout: {config.get('orchestrator', {}).get('default_timeout_seconds')}s")
                print(f"   Agents: {len([k for k in config.keys() if k != 'orchestrator' and k != 'common'])}")
            print()

if __name__ == "__main__":
    success = test_config_files()
    if success:
        print_config_summary()
    sys.exit(0 if success else 1)
