#!/usr/bin/env python3
"""
Route Extractor - Extracts route definitions from Python AST

Responsible for:
- Finding TurboX app instantiation
- Extracting @app.route() decorated functions
- Validating decorator patterns
"""
import ast
from typing import List, Dict


class RouteExtractor(ast.NodeVisitor):
    """Extracts route definitions from Python source code"""
    
    def __init__(self):
        self.routes: List[Dict] = []
        self.functions: Dict[str, ast.FunctionDef] = {}
        self.app_name = None
    
    def visit_Assign(self, node):
        """Find app = TurboX() assignment"""
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name) and node.value.func.id == 'TurboX':
                if node.targets and isinstance(node.targets[0], ast.Name):
                    self.app_name = node.targets[0].id
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        """Find functions with @app.route() decorators"""
        # Store all function definitions
        self.functions[node.name] = node
        
        # Check for @app.route decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    # Check if this is a route decorator
                    if decorator.func.attr == 'route':
                        # Verify it's decorating the TurboX instance, not some other object
                        # Must be a direct attribute access like app.route(), not app.router.route()
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
                        methods = ['GET']
                        
                        if decorator.args:
                            if isinstance(decorator.args[0], ast.Constant):
                                path = decorator.args[0].value
                        
                        # Check for methods keyword argument
                        for keyword in decorator.keywords:
                            if keyword.arg == 'methods':
                                if isinstance(keyword.value, ast.List):
                                    methods = [elt.value for elt in keyword.value.elts if isinstance(elt, ast.Constant)]
                        
                        if path:
                            self.routes.append({
                                'path': path,
                                'methods': methods,
                                'handler': node.name,
                                'function': node
                            })
        
        self.generic_visit(node)


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
