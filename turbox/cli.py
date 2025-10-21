#!/usr/bin/env python3
"""
TurboX CLI - Command line tool for building and running TurboX apps
"""
import sys
from turbox.build import build

def main():
    if len(sys.argv) < 2:
        print("TurboX - High-performance Python web framework")
        print("\nUsage:")
        print("  turbox build <app.py> [output]  - Build app to native binary")
        print("  turbox run <app.py>              - Build and run app")
        print("\nExamples:")
        print("  turbox build examples/hello.py")
        print("  turbox build examples/hello.py my_server")
        print("  turbox run examples/hello.py")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'build':
        if len(sys.argv) < 3:
            print("Error: Missing app file")
            print("Usage: turbox build <app.py> [output]")
            sys.exit(1)
        
        python_file = sys.argv[2]
        output_binary = sys.argv[3] if len(sys.argv) > 3 else None
        build(python_file, output_binary)
    
    elif command == 'run':
        if len(sys.argv) < 3:
            print("Error: Missing app file")
            print("Usage: turbox run <app.py>")
            sys.exit(1)
        
        python_file = sys.argv[2]
        output_binary = python_file.replace('.py', '_server')
        
        print("Building...")
        build(python_file, output_binary)
        
        print(f"\nStarting server...")
        import subprocess
        subprocess.run([f'./{output_binary}'])
    
    else:
        print(f"Unknown command: {command}")
        print("Available commands: build, run")
        sys.exit(1)

if __name__ == '__main__':
    main()
