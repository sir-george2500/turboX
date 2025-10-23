#!/usr/bin/env python3
"""
TurboX Build System - Main build orchestrator

The build tool bridges the Python API layer with the Nucleus server core:
1. Parses Python source using AST
2. Extracts route definitions and handler functions  
3. Validates application before compilation
4. Transpiles Python handlers to Codon
5. Generates complete Nucleus server with embedded routes
6. Compiles to native binary using Codon compiler

This is the main entry point that coordinates all build phases.
"""
import sys
from pathlib import Path
from typing import Optional

from ..validator import validate_app, print_validation_results
from .extractor import extract_routes
from .transpiler import generate_codon_server
from .compiler import compile_to_binary, check_codon_available

__all__ = ['build', 'extract_routes', 'generate_codon_server', 'compile_to_binary']


def build(python_file: str, output_binary: Optional[str] = None) -> None:
    """Build a TurboX app to native binary
    
    Orchestrates the complete build process:
    1. Extract routes from Python source
    2. Validate application structure
    3. Transpile to Codon code
    4. Compile to native binary
    
    Args:
        python_file: Path to Python application file
        output_binary: Optional output binary name (defaults to python_file without .py)
    """
    # Check prerequisites
    if not Path(python_file).exists():
        print(f"❌ Error: File {python_file} not found")
        sys.exit(1)
    
    if not check_codon_available():
        print(f"❌ Error: Codon compiler not found")
        print("Please install Codon: https://github.com/exaloop/codon")
        sys.exit(1)
    
    # Read source code
    with open(python_file, 'r') as f:
        source_code = f.read()
    
    # Phase 1: Extract routes
    print(f"📋 Extracting routes from {python_file}...")
    routes = extract_routes(python_file)
    
    if not routes:
        print("⚠️  No routes found in the file")
        print("Make sure you have:")
        print("  1. app = TurboX()")
        print("  2. Functions decorated with @app.route('/path')")
        sys.exit(1)
    
    print(f"Found {len(routes)} route(s):")
    for route in routes:
        methods_str = ', '.join(route['methods'])
        print(f"  [{methods_str}] {route['path']} -> {route['handler']}")
    
    # Phase 2: Validate BEFORE compilation
    print(f"\n🔍 Validating application...")
    errors, warnings = validate_app(python_file, source_code, routes)
    
    has_errors = print_validation_results(errors, warnings)
    
    if has_errors:
        print("\n❌ Build failed due to validation errors.")
        print("Fix the errors above and try again.\n")
        sys.exit(1)
    
    if not errors and not warnings:
        print("✅ Validation passed!")
    elif warnings and not errors:
        print("✅ Validation passed with warnings")
    
    # Phase 3: Generate Codon server
    generated_file = python_file.replace('.py', '_generated.codon')
    generate_codon_server(routes, generated_file)
    
    # Phase 4: Compile with Codon
    if output_binary is None:
        output_binary = python_file.replace('.py', '')
    
    success = compile_to_binary(generated_file, output_binary)
    
    if not success:
        sys.exit(1)
