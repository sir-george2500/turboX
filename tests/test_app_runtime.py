#!/usr/bin/env python3
"""
Tests for TurboX app runtime - HTTP method decorators
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from turbox import TurboX, Request


def test_http_method_decorators_registration():
    """Test that HTTP method decorators register routes correctly"""
    app = TurboX()
    
    @app.get("/get")
    def get_handler(request):
        return "GET"
    
    @app.post("/post")
    def post_handler(request):
        return "POST"
    
    @app.put("/put")
    def put_handler(request):
        return "PUT"
    
    @app.delete("/delete")
    def delete_handler(request):
        return "DELETE"
    
    @app.patch("/patch")
    def patch_handler(request):
        return "PATCH"
    
    @app.head("/head")
    def head_handler(request):
        return "HEAD"
    
    @app.options("/options")
    def options_handler(request):
        return "OPTIONS"
    
    # Verify all routes are registered
    assert ("GET", "/get") in app.routes
    assert ("POST", "/post") in app.routes
    assert ("PUT", "/put") in app.routes
    assert ("DELETE", "/delete") in app.routes
    assert ("PATCH", "/patch") in app.routes
    assert ("HEAD", "/head") in app.routes
    assert ("OPTIONS", "/options") in app.routes
    
    assert len(app.routes) == 7
    
    print("✅ test_http_method_decorators_registration passed")


def test_decorator_returns_function():
    """Test that decorators return the original function"""
    app = TurboX()
    
    @app.get("/test")
    def handler(request):
        return "test"
    
    # Decorator should return the original function
    assert handler.__name__ == "handler"
    assert handler(None) == "test"
    
    print("✅ test_decorator_returns_function passed")


def test_same_path_different_methods():
    """Test same path with different HTTP methods"""
    app = TurboX()
    
    @app.get("/resource")
    def get_resource(request):
        return "GET resource"
    
    @app.post("/resource")
    def create_resource(request):
        return "POST resource"
    
    @app.put("/resource")
    def update_resource(request):
        return "PUT resource"
    
    @app.delete("/resource")
    def delete_resource(request):
        return "DELETE resource"
    
    # All should be registered with same path but different methods
    assert len(app.routes) == 4
    assert ("GET", "/resource") in app.routes
    assert ("POST", "/resource") in app.routes
    assert ("PUT", "/resource") in app.routes
    assert ("DELETE", "/resource") in app.routes
    
    # Each should call the correct handler
    assert app.routes[("GET", "/resource")](None) == "GET resource"
    assert app.routes[("POST", "/resource")](None) == "POST resource"
    assert app.routes[("PUT", "/resource")](None) == "PUT resource"
    assert app.routes[("DELETE", "/resource")](None) == "DELETE resource"
    
    print("✅ test_same_path_different_methods passed")


def test_route_decorator_still_works():
    """Test that @app.route() still works alongside HTTP method decorators"""
    app = TurboX()
    
    @app.route("/old-style", methods=["GET", "POST"])
    def old_style(request):
        return "old style"
    
    @app.get("/new-style")
    def new_style(request):
        return "new style"
    
    # Both should work
    assert len(app.routes) == 3  # GET+POST for old-style, GET for new-style
    assert ("GET", "/old-style") in app.routes
    assert ("POST", "/old-style") in app.routes
    assert ("GET", "/new-style") in app.routes
    
    print("✅ test_route_decorator_still_works passed")


def run_all_tests():
    """Run all runtime tests"""
    print("\n" + "="*60)
    print("Running TurboX Runtime Tests - HTTP Method Decorators")
    print("="*60 + "\n")
    
    tests = [
        test_http_method_decorators_registration,
        test_decorator_returns_function,
        test_same_path_different_methods,
        test_route_decorator_still_works,
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
        print(f"✅ All {len(tests)} runtime tests passed!")
    else:
        print(f"❌ {failed}/{len(tests)} tests failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
