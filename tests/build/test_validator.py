#!/usr/bin/env python3
"""
Tests for Validator
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from turbox.validator import validate_app, ValidationError, ValidationWarning
import ast


def test_valid_handler():
    """Test validation of a correct handler"""
    code = """
from turbox import TurboX, Request

app = TurboX()

@app.route("/hello")
def hello(request: Request) -> str:
    return "Hello, World!"
"""
    
    tree = ast.parse(code)
    from turbox.build.extractor import RouteExtractor
    extractor = RouteExtractor()
    extractor.visit(tree)
    
    errors, warnings = validate_app("test.py", code, extractor.routes)
    
    assert len(errors) == 0, f"Expected no errors, got {len(errors)}"
    
    print("✅ test_valid_handler passed")


def test_missing_type_hints():
    """Test validation warns about missing type hints"""
    code = """
from turbox import TurboX

app = TurboX()

@app.route("/hello")
def hello(request):
    return "Hello, World!"
"""
    
    tree = ast.parse(code)
    from turbox.build.extractor import RouteExtractor
    extractor = RouteExtractor()
    extractor.visit(tree)
    
    errors, warnings = validate_app("test.py", code, extractor.routes)
    
    # Should have warnings about missing type hints
    assert len(warnings) > 0, "Expected warnings about missing type hints"
    
    print("✅ test_missing_type_hints passed")


def test_wrong_return_type():
    """Test validation catches wrong return types"""
    code = """
from turbox import TurboX, Request

app = TurboX()

@app.route("/age")
def get_age(request: Request) -> int:
    return 25
"""
    
    tree = ast.parse(code)
    from turbox.build.extractor import RouteExtractor
    extractor = RouteExtractor()
    extractor.visit(tree)
    
    errors, warnings = validate_app("test.py", code, extractor.routes)
    
    # Should have error about wrong return type
    assert len(errors) > 0, "Expected error about return type"
    assert any('must return' in e.message and 'str' in e.message for e in errors)
    
    print("✅ test_wrong_return_type passed")


def test_unsupported_imports():
    """Test validation catches unsupported imports"""
    code = """
from turbox import TurboX
import json

app = TurboX()

@app.route("/data")
def get_data(request):
    return json.dumps({"key": "value"})
"""
    
    tree = ast.parse(code)
    from turbox.build.extractor import RouteExtractor
    extractor = RouteExtractor()
    extractor.visit(tree)
    
    errors, warnings = validate_app("test.py", code, extractor.routes)
    
    # Should have error about unsupported json import
    assert len(errors) > 0, "Expected error about json import"
    assert any('json' in e.message.lower() for e in errors)
    
    print("✅ test_unsupported_imports passed")


def test_non_string_return_value():
    """Test validation catches non-string return values"""
    code = """
from turbox import TurboX, Request

app = TurboX()

@app.route("/number")
def get_number(request: Request) -> str:
    return 42
"""
    
    tree = ast.parse(code)
    from turbox.build.extractor import RouteExtractor
    extractor = RouteExtractor()
    extractor.visit(tree)
    
    errors, warnings = validate_app("test.py", code, extractor.routes)
    
    # Should have error about returning int instead of str
    assert len(errors) > 0, "Expected error about non-string return"
    assert any('int' in e.message for e in errors)
    
    print("✅ test_non_string_return_value passed")


def run_all_tests():
    """Run all validator tests"""
    print("\n" + "="*60)
    print("Running Validator Tests")
    print("="*60 + "\n")
    
    tests = [
        test_valid_handler,
        test_missing_type_hints,
        test_wrong_return_type,
        test_unsupported_imports,
        test_non_string_return_value,
    ]
    
    failed = 0
    for test in tests:
        try:
            test()
        except AssertionError as e:
            print(f"❌ {test.__name__} FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} ERROR: {e}")
            failed += 1
    
    print("\n" + "="*60)
    if failed == 0:
        print(f"✅ All {len(tests)} tests passed!")
    else:
        print(f"❌ {failed}/{len(tests)} tests failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
