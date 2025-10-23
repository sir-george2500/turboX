#!/usr/bin/env python3
"""
Route Extractor - Extracts route definitions from Python AST

Responsible for:
- Finding TurboX app instantiation
- Extracting @app.route() and @app.get/post/put/delete/patch() decorated functions
- Validating decorator patterns
- Attempting to resolve computed/dynamic routes
"""
import ast
from typing import List, Dict, Optional

# Supported HTTP method decorators
SUPPORTED_DECORATORS = ['route', 'get', 'post', 'put', 'delete', 'patch', 'head', 'options']


class RouteExtractor(ast.NodeVisitor):
    """Extracts route definitions from Python source code"""
    
    def __init__(self):
        self.routes: List[Dict] = []
        self.functions: Dict[str, ast.FunctionDef] = {}
        self.app_name = None
        self.constants: Dict[str, str] = {}  # Store module-level constants
    
    def visit_Assign(self, node):
        """Find app = TurboX() assignment and track constants"""
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name) and node.value.func.id == 'TurboX':
                if node.targets and isinstance(node.targets[0], ast.Name):
                    self.app_name = node.targets[0].id
        
        # Track module-level string constants for dynamic route resolution
        if node.targets and isinstance(node.targets[0], ast.Name):
            var_name = node.targets[0].id
            if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                self.constants[var_name] = node.value.value
        
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Find functions with @app.route() decorators"""
        # Store all function definitions
        self.functions[node.name] = node
        
        # Check for @app.route, @app.get, @app.post, etc. decorators
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    # Check if this is a supported HTTP decorator
                    if decorator.func.attr in SUPPORTED_DECORATORS:
                        # Verify it's decorating the TurboX instance, not some other object
                        # Must be a direct attribute access like app.get(), not app.router.get()
                        if not isinstance(decorator.func.value, ast.Name):
                            # Skip nested attributes like app.router.route()
                            continue
                        
                        decorator_obj = decorator.func.value.id
                        
                        # If we found the app name, verify it matches
                        if self.app_name and decorator_obj != self.app_name:
                            # Skip this decorator - it's not our TurboX app
                            continue
                        
                        # Extract route path
                        path = None
                        methods = ['GET']  # default for @app.route()
                        
                        if decorator.args:
                            # Try to evaluate the path (handles constants and simple expressions)
                            path = self._try_evaluate_path(decorator.args[0])
                        
                        # Determine HTTP methods
                        decorator_name = decorator.func.attr
                        
                        if decorator_name == 'route':
                            # For @app.route(), check for methods keyword argument
                            for keyword in decorator.keywords:
                                if keyword.arg == 'methods':
                                    if isinstance(keyword.value, ast.List):
                                        methods = [elt.value for elt in keyword.value.elts if isinstance(elt, ast.Constant)]
                        else:
                            # For @app.get(), @app.post(), etc.
                            # Infer HTTP method from decorator name
                            methods = [decorator_name.upper()]
                        
                        if path:
                            self.routes.append({
                                'path': path,
                                'methods': methods,
                                'handler': node.name,
                                'function': node
                            })
        
        self.generic_visit(node)
    
    def _try_evaluate_path(self, path_node: ast.AST) -> Optional[str]:
        """Try to evaluate a path expression to a string constant
        
        Supports:
        - String constants: "/path"
        - String concatenation: BASE + "/users"
        - F-strings with constants: f"/api/{VERSION}/users"
        - Variable references to constants
        """
        # Simple constant
        if isinstance(path_node, ast.Constant):
            return str(path_node.value)
        
        # Binary operation (string concatenation with +)
        if isinstance(path_node, ast.BinOp) and isinstance(path_node.op, ast.Add):
            left = self._try_evaluate_path(path_node.left)
            right = self._try_evaluate_path(path_node.right)
            if left is not None and right is not None:
                return left + right
            return None
        
        # F-string (JoinedStr)
        if isinstance(path_node, ast.JoinedStr):
            result = []
            for value in path_node.values:
                if isinstance(value, ast.Constant):
                    result.append(str(value.value))
                elif isinstance(value, ast.FormattedValue):
                    # Try to evaluate the formatted value
                    val = self._try_evaluate_path(value.value)
                    if val is not None:
                        result.append(val)
                    else:
                        return None  # Can't resolve
            return ''.join(result)
        
        # Name lookup - check our constants dict
        if isinstance(path_node, ast.Name):
            return self.constants.get(path_node.id)
        
        return None


def extract_routes(python_file: str) -> List[Dict]:
    """Extract routes from a Python file
    
    Args:
        python_file: Path to Python source file
        
    Returns:
        List of route dictionaries with keys: path, methods, handler, function
    """
    with open(python_file, 'r') as f:
        tree = ast.parse(f.read())
    
    extractor = RouteExtractor()
    extractor.visit(tree)
    
    return extractor.routes
