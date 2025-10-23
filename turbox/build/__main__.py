#!/usr/bin/env python3
"""
TurboX Build Tool - Command-line entry point

Allows running the build system via: python -m turbox.build
"""
import sys
from . import build


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python -m turbox.build <app.py> [output_binary]")
        sys.exit(1)
    
    python_file = sys.argv[1]
    output_binary = sys.argv[2] if len(sys.argv) > 2 else None
    
    build(python_file, output_binary)
