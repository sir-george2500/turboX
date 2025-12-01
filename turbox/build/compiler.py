#!/usr/bin/env python3
"""
Codon Compiler - Handles compilation of generated Codon code to native binary

Responsible for:
- Running Codon compiler
- Handling compilation errors
- Managing output binaries
"""
import subprocess
import sys
import os
from pathlib import Path


def compile_to_binary(codon_file: str, output_binary: str) -> bool:
    """Compile Codon source file to native binary
    
    Args:
        codon_file: Path to .codon source file
        output_binary: Path to output binary
        
    Returns:
        True if compilation succeeded, False otherwise
    """
    print(f"\n🔨 Compiling with Codon...")
    
    result = subprocess.run(
        ['codon', 'build', '-o', output_binary, codon_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ Successfully built: {output_binary}")
        print(f"\nRun your server: ./{output_binary}")
        return True
    else:
        print(f"❌ Compilation failed:")
        print(result.stderr)
        return False


def check_codon_available() -> bool:
    """Check if Codon compiler is available
    
    Returns:
        True if Codon is available, False otherwise
    """
    try:
        result = subprocess.run(
            ['codon', '--version'],
            capture_output=True,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        return False
