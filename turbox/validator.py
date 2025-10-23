#!/usr/bin/env python3
"""
TurboX Validation Layer

Validates Python applications before transpilation to Codon.
Catches errors early with helpful messages instead of cryptic compiler errors.
"""
import ast
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ValidationError:
    """Represents a validation error with context"""
    message: str
    line: Optional[int] = None
    column: Optional[int] = None
    file: Optional[str] = None
    suggestion: Optional[str] = None
    code_context: Optional[str] = None


@dataclass
class ValidationWarning:
    """Represents a validation warning"""
    message: str
    line: Optional[int] = None
    file: Optional[str] = None


class AppValidator:
    """Validates TurboX applications before compilation"""
    
    def __init__(self, source_file: str, source_code: str, routes: List[Dict]):
        self.source_file = source_file
        self.source_code = source_code
        self.source_lines = source_code.split('\n')
        self.routes = routes
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationWarning] = []
        self.tree = ast.parse(source_code)
    
    def validate(self) -> Tuple[List[ValidationError], List[ValidationWarning]]:
        """Run all validation checks"""
        self._validate_routes_exist()
        self._validate_handler_signatures()
        self._validate_return_types()
        self._validate_unsupported_features()
        self._validate_imports()
        self._detect_dynamic_routes()
        
        return self.errors, self.warnings
    
    def _validate_routes_exist(self):
        """Check that all routes have valid handler functions"""
        for route in self.routes:
            handler_name = route.get('handler')
            func_node = route.get('function')
            
            if not func_node:
                self.errors.append(ValidationError(
                    message=f"Handler function '{handler_name}' not found",
                    suggestion="Ensure the function is defined in the same file"
                ))
    
    def _validate_handler_signatures(self):
        """Validate that handler functions have correct signatures"""
        for route in self.routes:
            func_node = route.get('function')
            if not func_node:
                continue
            
            handler_name = route['handler']
            
            # Check parameter count
            if len(func_node.args.args) != 1:
                self.errors.append(ValidationError(
                    message=f"Handler '{handler_name}' must accept exactly one parameter (request)",
                    line=func_node.lineno,
                    file=self.source_file,
                    code_context=self._get_code_context(func_node.lineno),
                    suggestion=f"def {handler_name}(request: Request) -> str:"
                ))
                continue
            
            # Check parameter name
            param = func_node.args.args[0]
            param_name = param.arg
            
            # Check for type annotation on parameter
            if not param.annotation:
                self.warnings.append(ValidationWarning(
                    message=f"Handler '{handler_name}' parameter '{param_name}' missing type hint",
                    line=func_node.lineno,
                    file=self.source_file
                ))
            elif isinstance(param.annotation, ast.Name) and param.annotation.id != 'Request':
                self.errors.append(ValidationError(
                    message=f"Handler '{handler_name}' parameter must be of type 'Request', got '{param.annotation.id}'",
                    line=func_node.lineno,
                    file=self.source_file,
                    code_context=self._get_code_context(func_node.lineno),
                    suggestion=f"def {handler_name}(request: Request) -> str:"
                ))
            
            # Check return type annotation
            if not func_node.returns:
                self.warnings.append(ValidationWarning(
                    message=f"Handler '{handler_name}' missing return type hint",
                    line=func_node.lineno,
                    file=self.source_file
                ))
            elif isinstance(func_node.returns, ast.Name) and func_node.returns.id != 'str':
                self.errors.append(ValidationError(
                    message=f"Handler '{handler_name}' must return 'str', got '{func_node.returns.id}'",
                    line=func_node.lineno,
                    file=self.source_file,
                    code_context=self._get_code_context(func_node.lineno),
                    suggestion="Handlers must return strings. Use str() to convert other types."
                ))
    
    def _validate_return_types(self):
        """Check that handlers return strings"""
        for route in self.routes:
            func_node = route.get('function')
            if not func_node:
                continue
            
            handler_name = route['handler']
            
            # Find all return statements
            returns = [node for node in ast.walk(func_node) if isinstance(node, ast.Return)]
            
            if not returns:
                self.errors.append(ValidationError(
                    message=f"Handler '{handler_name}' has no return statement",
                    line=func_node.lineno,
                    file=self.source_file,
                    code_context=self._get_code_context(func_node.lineno),
                    suggestion="Add a return statement that returns a string"
                ))
                continue
            
            # Check each return statement
            for ret_node in returns:
                if not ret_node.value:
                    self.errors.append(ValidationError(
                        message=f"Handler '{handler_name}' has empty return statement",
                        line=ret_node.lineno,
                        file=self.source_file,
                        code_context=self._get_code_context(ret_node.lineno),
                        suggestion="Return a string value"
                    ))
                    continue
                
                # Check if return value is obviously not a string
                if isinstance(ret_node.value, ast.Constant):
                    if not isinstance(ret_node.value.value, str):
                        self.errors.append(ValidationError(
                            message=f"Handler '{handler_name}' returns non-string value: {type(ret_node.value.value).__name__}",
                            line=ret_node.lineno,
                            file=self.source_file,
                            code_context=self._get_code_context(ret_node.lineno),
                            suggestion=f"Convert to string: return str({ret_node.value.value})"
                        ))
    
    def _validate_unsupported_features(self):
        """Check for Python features not supported in Codon"""
        unsupported_imports = {
            'json': 'JSON module not available in Codon',
            'requests': 'HTTP client not available in Codon',
            'asyncio': 'Async/await not supported',
            'threading': 'Threading module not available',
            'multiprocessing': 'Multiprocessing not available',
        }
        
        for node in ast.walk(self.tree):
            # Check imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                module_name = None
                if isinstance(node, ast.Import):
                    if node.names:
                        module_name = node.names[0].name.split('.')[0]
                elif isinstance(node, ast.ImportFrom):
                    module_name = node.module.split('.')[0] if node.module else None
                
                if module_name in unsupported_imports:
                    self.errors.append(ValidationError(
                        message=f"Unsupported import: {module_name}",
                        line=node.lineno,
                        file=self.source_file,
                        code_context=self._get_code_context(node.lineno),
                        suggestion=unsupported_imports[module_name]
                    ))
            
            # Check for async functions
            if isinstance(node, ast.AsyncFunctionDef):
                self.errors.append(ValidationError(
                    message=f"Async functions not supported: {node.name}",
                    line=node.lineno,
                    file=self.source_file,
                    code_context=self._get_code_context(node.lineno),
                    suggestion="Use regular functions instead"
                ))
            
            # Check for lambda functions (warning)
            if isinstance(node, ast.Lambda):
                self.warnings.append(ValidationWarning(
                    message="Lambda functions may not work correctly in Codon",
                    line=node.lineno,
                    file=self.source_file
                ))
    
    def _validate_imports(self):
        """Validate that required imports are present"""
        has_turbox_import = False
        has_request_import = False
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.ImportFrom):
                if node.module == 'turbox':
                    has_turbox_import = True
                    for alias in node.names:
                        if alias.name == 'Request':
                            has_request_import = True
        
        if not has_turbox_import:
            self.warnings.append(ValidationWarning(
                message="Missing 'from turbox import TurboX' import",
                file=self.source_file
            ))
        
        # Check if Request type is used but not imported
        for route in self.routes:
            func_node = route.get('function')
            if func_node and func_node.args.args:
                param = func_node.args.args[0]
                if param.annotation and isinstance(param.annotation, ast.Name):
                    if param.annotation.id == 'Request' and not has_request_import:
                        self.warnings.append(ValidationWarning(
                            message="Using 'Request' type but not importing it. Add: from turbox import Request",
                            line=func_node.lineno,
                            file=self.source_file
                        ))
    
    def _detect_dynamic_routes(self):
        """Detect and attempt to resolve dynamic route paths"""
        # This catches routes that weren't extracted (e.g., in loops, conditionals)
        # We'll scan for decorators that might have dynamic paths
        
        for node in ast.walk(self.tree):
            if isinstance(node, ast.FunctionDef):
                for decorator in node.decorator_list:
                    if isinstance(decorator, ast.Call):
                        if isinstance(decorator.func, ast.Attribute):
                            # Check if this looks like a route decorator
                            if decorator.func.attr in ['route', 'get', 'post', 'put', 'delete', 'patch', 'head', 'options']:
                                if decorator.args:
                                    path_arg = decorator.args[0]
                                    
                                    # Check if path is non-constant
                                    if not isinstance(path_arg, ast.Constant):
                                        # Try to evaluate it
                                        try:
                                            # Attempt constant evaluation
                                            evaluated = self._try_evaluate_expression(path_arg)
                                            if evaluated is None:
                                                # Could not evaluate - warn user
                                                self.warnings.append(ValidationWarning(
                                                    message=f"Dynamic route path in '{node.name}' - path cannot be determined at build time",
                                                    line=node.lineno,
                                                    file=self.source_file
                                                ))
                                        except:
                                            self.warnings.append(ValidationWarning(
                                                message=f"Complex route path in '{node.name}' - may not work correctly",
                                                line=node.lineno,
                                                file=self.source_file
                                            ))
    
    def _try_evaluate_expression(self, node: ast.AST) -> Optional[str]:
        """Try to evaluate a constant expression
        
        Supports:
        - String constants
        - String concatenation with +
        - F-strings with constant values
        - Name lookups of module-level constants
        """
        # Simple constant
        if isinstance(node, ast.Constant):
            return str(node.value)
        
        # Binary operation (string concatenation)
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
            left = self._try_evaluate_expression(node.left)
            right = self._try_evaluate_expression(node.right)
            if left is not None and right is not None:
                return left + right
            return None
        
        # F-string (JoinedStr)
        if isinstance(node, ast.JoinedStr):
            result = []
            for value in node.values:
                if isinstance(value, ast.Constant):
                    result.append(str(value.value))
                elif isinstance(value, ast.FormattedValue):
                    # Try to evaluate the formatted value
                    val = self._try_evaluate_expression(value.value)
                    if val is not None:
                        result.append(val)
                    else:
                        return None
            return ''.join(result)
        
        # Name lookup - try to find constant assignment
        if isinstance(node, ast.Name):
            return self._lookup_constant(node.id)
        
        return None
    
    def _lookup_constant(self, name: str) -> Optional[str]:
        """Look up a module-level constant"""
        for node in ast.walk(self.tree):
            if isinstance(node, ast.Assign):
                # Check if this is a simple assignment like: VAR = "value"
                if node.targets and isinstance(node.targets[0], ast.Name):
                    if node.targets[0].id == name:
                        if isinstance(node.value, ast.Constant):
                            return str(node.value.value)
        return None
    
    def _get_code_context(self, line_num: int, context_lines: int = 2) -> str:
        """Get source code context around a line"""
        if not self.source_lines or line_num < 1:
            return ""
        
        start = max(0, line_num - context_lines - 1)
        end = min(len(self.source_lines), line_num + context_lines)
        
        lines = []
        for i in range(start, end):
            prefix = ">>> " if i == line_num - 1 else "    "
            lines.append(f"{prefix}{self.source_lines[i]}")
        
        return "\n".join(lines)


def validate_app(source_file: str, source_code: str, routes: List[Dict]) -> Tuple[List[ValidationError], List[ValidationWarning]]:
    """Validate a TurboX application
    
    Args:
        source_file: Path to the source file
        source_code: Source code content
        routes: Extracted routes from the application
    
    Returns:
        Tuple of (errors, warnings)
    """
    validator = AppValidator(source_file, source_code, routes)
    return validator.validate()


def print_validation_results(errors: List[ValidationError], warnings: List[ValidationWarning]) -> bool:
    """Print validation errors and warnings in a user-friendly format
    
    Returns:
        True if there are errors, False otherwise
    """
    if warnings:
        print("\n⚠️  Warnings:")
        for warning in warnings:
            location = f" ({warning.file}:{warning.line})" if warning.line else ""
            print(f"  • {warning.message}{location}")
    
    if errors:
        print("\n❌ Validation Errors:\n")
        for i, error in enumerate(errors, 1):
            print(f"{i}. {error.message}")
            
            if error.file and error.line:
                print(f"   Location: {error.file}:{error.line}")
            
            if error.code_context:
                print(f"\n{error.code_context}\n")
            
            if error.suggestion:
                print(f"   💡 Suggestion: {error.suggestion}")
            
            print()
        
        return True
    
    return False
