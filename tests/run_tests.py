#!/usr/bin/env python3
"""
Master test runner for all build system tests
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import test modules
from tests.build import test_route_extractor, test_transpiler, test_validator, test_computed_routes
from tests import test_app_runtime


def main():
    """Run all test suites"""
    print("\n" + "="*70)
    print(" TurboX Build System - Test Suite")
    print("="*70)
    
    results = []
    
    # Run each test suite
    print("\n📦 Running Route Extractor Tests...")
    results.append(("Route Extractor", test_route_extractor.run_all_tests()))
    
    print("\n📦 Running Transpiler Tests...")
    results.append(("Transpiler", test_transpiler.run_all_tests()))
    
    print("\n📦 Running Validator Tests...")
    results.append(("Validator", test_validator.run_all_tests()))
    
    print("\n📦 Running Runtime Tests...")
    results.append(("Runtime", test_app_runtime.run_all_tests()))
    
    print("\n📦 Running Computed Routes Tests...")
    results.append(("Computed Routes", test_computed_routes.run_all_tests()))
    
    # Summary
    print("\n" + "="*70)
    print(" Test Summary")
    print("="*70)
    
    all_passed = True
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name:30} {status}")
        if not passed:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n🎉 All test suites passed!\n")
        return 0
    else:
        print("\n❌ Some tests failed\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())
