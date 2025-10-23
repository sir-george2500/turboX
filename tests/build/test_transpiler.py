#!/usr/bin/env python3
"""
Tests for Code Transpiler
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from turbox.build.transpiler import generate_handler_code, generate_nucleus_template
import ast


def test_simple_string_return():
    """Test transpiling a simple string return"""
    code = """
def hello(request):
    return "Hello, World!"
"""
    tree = ast.parse(code)
    func = tree.body[0]
    
    route = {
        'handler': 'hello',
        'function': func
    }
    
    result = generate_handler_code(route)
    
    assert 'def hello(request: Request) -> str:' in result
    assert 'return "Hello, World!"' in result
    
    print("✅ test_simple_string_return passed")


def test_nucleus_template_generation():
    """Test that Nucleus template is generated"""
    template = generate_nucleus_template()
    
    # Check for key components
    assert 'class Request:' in template
    assert 'class TurboX:' in template
    assert 'def parse_request' in template
    assert 'def build_response' in template
    assert 'from C import' in template
    
    print("✅ test_nucleus_template_generation passed")


def test_handler_with_no_return():
    """Test handler with no return statement"""
    code = """
def broken(request):
    pass
"""
    tree = ast.parse(code)
    func = tree.body[0]
    
    route = {
        'handler': 'broken',
        'function': func
    }
    
    result = generate_handler_code(route)
    
    # Should have fallback return
    assert 'return "Response from broken"' in result
    
    print("✅ test_handler_with_no_return passed")


def run_all_tests():
    """Run all transpiler tests"""
    print("\n" + "="*60)
    print("Running Transpiler Tests")
    print("="*60 + "\n")
    
    tests = [
        test_simple_string_return,
        test_nucleus_template_generation,
        test_handler_with_no_return,
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
