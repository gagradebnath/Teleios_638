#!/usr/bin/env python3
"""
Master test runner for τέλειος backend.
Runs all test suites in sequence and provides comprehensive reporting.

Usage:
    python run_tests.py [--quick] [--verbose]
    
Options:
    --quick     Skip slow tests (database, services)
    --verbose   Show detailed output from each test
"""
import argparse
import subprocess
import sys
from pathlib import Path
from datetime import datetime

BACKEND_DIR = Path(__file__).parent

TEST_SUITES = [
    {
        "name": "Import Tests",
        "script": "test_imports.py",
        "description": "Verify all Python modules can be imported",
        "quick": True,
    },
    {
        "name": "Config Tests",
        "script": "test_config.py",
        "description": "Verify all JSON config files are valid",
        "quick": True,
    },
    {
        "name": "Basic Functionality Tests",
        "script": "test_basic.py",
        "description": "Test core services and components",
        "quick": False,
    },
]


def run_test_suite(suite: dict, verbose: bool = False) -> bool:
    """Run a single test suite."""
    script_path = BACKEND_DIR / suite["script"]
    
    if not script_path.exists():
        print(f"   ⚠️  Test script not found: {suite['script']}")
        return False
    
    print(f"\n{'='*60}")
    print(f"Running: {suite['name']}")
    print(f"Description: {suite['description']}")
    print(f"{'='*60}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            cwd=BACKEND_DIR,
            capture_output=not verbose,
            text=True,
            timeout=60,
        )
        
        if result.returncode == 0:
            print(f"\n✅ {suite['name']} PASSED")
            if not verbose and result.stdout:
                # Show summary line only
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'SUCCESS' in line or 'PASS' in line:
                        print(f"   {line}")
            return True
        else:
            print(f"\n❌ {suite['name']} FAILED")
            if not verbose and result.stdout:
                print(result.stdout)
            if result.stderr:
                print("STDERR:", result.stderr)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"\n❌ {suite['name']} TIMEOUT (>60s)")
        return False
    except Exception as e:
        print(f"\n❌ {suite['name']} ERROR: {e}")
        return False


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(description="τέλειος Backend Test Runner")
    parser.add_argument("--quick", action="store_true", help="Run only quick tests")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    args = parser.parse_args()
    
    print("="*60)
    print("τέλειος Backend Test Runner")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Filter suites
    suites_to_run = TEST_SUITES
    if args.quick:
        suites_to_run = [s for s in TEST_SUITES if s.get("quick", False)]
        print(f"\n⚡ Quick mode: Running {len(suites_to_run)} fast tests")
    
    # Run all test suites
    results = []
    for suite in suites_to_run:
        success = run_test_suite(suite, verbose=args.verbose)
        results.append((suite["name"], success))
    
    # Final summary
    print("\n" + "="*60)
    print("FINAL TEST SUMMARY")
    print("="*60 + "\n")
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} - {name}")
    
    print(f"\n{'='*60}")
    print(f"Results: {passed}/{total} test suites passed")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Backend is ready for deployment.")
        return 0
    else:
        print(f"\n⚠️  {total - passed} TEST SUITE(S) FAILED")
        print("Review the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
