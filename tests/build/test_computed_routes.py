#!/usr/bin/env python3
"""
Tests for computed/dynamic routes support
"""
import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from turbox.build.extractor import RouteExtractor


def test_simple_constant_route():
    """Test basic constant path (baseline)"""
    code = """
from turbox import TurboX

app = TurboX()

@app.get("/users")
def get_users(request):
    return "Users"
"""
    
    tree = ast.parse(code)
    extractor = RouteExtractor()
    extractor.visit(tree)
    
    assert len(extractor.routes) == 1
    assert extractor.routes[0]['path'] == '/users'
    
    print("✅ test_simple_constant_route passed")


def test_string_concatenation():
    """Test path with string concatenation"""
    code = """
from turbox import TurboX

app = TurboX()

BASE = "/api"

@app.get(BASE + "/users")
def get_users(request):
    return "Users"

@app.post(BASE + "/posts")
def get_posts(request):
    return "Posts"
"""
    
    tree = ast.parse(code)
    extractor = RouteExtractor()
    extractor.visit(tree)
    
    assert len(extractor.routes) == 2
    assert extractor.routes[0]['path'] == '/api/users'
    assert extractor.routes[1]['path'] == '/api/posts'
    
    print("✅ test_string_concatenation passed")


def test_fstring_with_constant():
    """Test f-string paths with constant values"""
    code = """
from turbox import TurboX

app = TurboX()

VERSION = "v1"
RESOURCE = "users"

@app.get(f"/api/{VERSION}/{RESOURCE}")
def get_users(request):
    return "Users"
"""
    
    tree = ast.parse(code)
    extractor = RouteExtractor()
    extractor.visit(tree)
    
    assert len(extractor.routes) == 1
    assert extractor.routes[0]['path'] == '/api/v1/users'
    
    print("✅ test_fstring_with_constant passed")


def test_multiple_concatenations():
    """Test complex string concatenation"""
    code = """
from turbox import TurboX

app = TurboX()

BASE = "/api"
VERSION = "/v1"
SUFFIX = "/list"

@app.get(BASE + VERSION + "/users" + SUFFIX)
def get_users(request):
    return "Users"
"""
    
    tree = ast.parse(code)
    extractor = RouteExtractor()
    extractor.visit(tree)
    
    assert len(extractor.routes) == 1
    assert extractor.routes[0]['path'] == '/api/v1/users/list'
    
    print("✅ test_multiple_concatenations passed")


def test_mixed_constant_styles():
    """Test mixing constants, f-strings, and concatenation"""
    code = """
from turbox import TurboX

app = TurboX()

API_BASE = "/api"
VERSION = "v2"

@app.get("/users")
def simple(request):
    return "Simple"

@app.get(API_BASE + "/posts")
def concat(request):
    return "Concat"

@app.get(f"/api/{VERSION}/comments")
def fstring(request):
    return "F-string"
"""
    
    tree = ast.parse(code)
    extractor = RouteExtractor()
    extractor.visit(tree)
    
    assert len(extractor.routes) == 3
    assert extractor.routes[0]['path'] == '/users'
    assert extractor.routes[1]['path'] == '/api/posts'
    assert extractor.routes[2]['path'] == '/api/v2/comments'
    
    print("✅ test_mixed_constant_styles passed")


def test_complex_fstring():
    """Test f-string with multiple interpolations"""
    code = """
from turbox import TurboX

app = TurboX()

API = "api"
VERSION = "v1"
RESOURCE = "users"

@app.get(f"/{API}/{VERSION}/{RESOURCE}/list")
def get_users(request):
    return "Users"
"""
    
    tree = ast.parse(code)
    extractor = RouteExtractor()
    extractor.visit(tree)
    
    assert len(extractor.routes) == 1
    assert extractor.routes[0]['path'] == '/api/v1/users/list'
    
    print("✅ test_complex_fstring passed")


def test_unresolvable_path_skipped():
    """Test that truly dynamic paths are skipped (not extracted)"""
    code = """
from turbox import TurboX

app = TurboX()

def get_path():
    return "/dynamic"

@app.get(get_path())  # Cannot resolve at build time
def dynamic_handler(request):
    return "Dynamic"

@app.get("/static")  # This one should work
def static_handler(request):
    return "Static"
"""
    
    tree = ast.parse(code)
    extractor = RouteExtractor()
    extractor.visit(tree)
    
    # Should only extract the static route
    assert len(extractor.routes) == 1
    assert extractor.routes[0]['path'] == '/static'
    assert extractor.routes[0]['handler'] == 'static_handler'
    
    print("✅ test_unresolvable_path_skipped passed")


def test_variable_from_import_not_resolved():
    """Test that imported variables are not resolved (safety)"""
    code = """
from turbox import TurboX
from config import BASE_PATH  # Can't resolve imported constants

app = TurboX()

@app.get(BASE_PATH + "/users")
def get_users(request):
    return "Users"
"""
    
    tree = ast.parse(code)
    extractor = RouteExtractor()
    extractor.visit(tree)
    
    # Should not extract since BASE_PATH is imported (not defined in module)
    assert len(extractor.routes) == 0
    
    print("✅ test_variable_from_import_not_resolved passed")


def test_constants_tracking():
    """Test that constants are properly tracked"""
    code = """
from turbox import TurboX

app = TurboX()

# These should be tracked
PATH_A = "/api"
PATH_B = "/v1"

# This should NOT be tracked (not a string constant)
PATH_C = 123

# This should NOT be tracked (function call)
PATH_D = some_function()
"""
    
    tree = ast.parse(code)
    extractor = RouteExtractor()
    extractor.visit(tree)
    
    # Check constants were tracked
    assert 'PATH_A' in extractor.constants
    assert extractor.constants['PATH_A'] == '/api'
    assert 'PATH_B' in extractor.constants
    assert extractor.constants['PATH_B'] == '/v1'
    
    # These should NOT be tracked
    assert 'PATH_C' not in extractor.constants
    assert 'PATH_D' not in extractor.constants
    
    print("✅ test_constants_tracking passed")


def run_all_tests():
    """Run all computed routes tests"""
    print("\n" + "="*60)
    print("Running Computed Routes Tests - Problem #3")
    print("="*60 + "\n")
    
    tests = [
        test_simple_constant_route,
        test_string_concatenation,
        test_fstring_with_constant,
        test_multiple_concatenations,
        test_mixed_constant_styles,
        test_complex_fstring,
        test_unresolvable_path_skipped,
        test_variable_from_import_not_resolved,
        test_constants_tracking,
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
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "="*60)
    if failed == 0:
        print(f"✅ All {len(tests)} tests passed!")
        print("Problem #3 (Computed routes) is PARTIALLY SOLVED! 🎉")
        print("Supports: constants, string concatenation, f-strings")
    else:
        print(f"❌ {failed}/{len(tests)} tests failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
