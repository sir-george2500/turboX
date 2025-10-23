# Build System Architecture

## Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      turbox/build.py                        │
│                   Main Orchestrator                         │
│                                                             │
│  build(python_file, output_binary)                         │
│    1. Check prerequisites                                   │
│    2. Extract routes          ──────────┐                  │
│    3. Validate app            ──────────┼──────┐           │
│    4. Generate Codon code     ──────────┼──────┼───┐       │
│    5. Compile binary          ──────────┼──────┼───┼───┐   │
└──────────────────────────────────────────┼──────┼───┼───┼───┘
                                           │      │   │   │
                    ┌──────────────────────┘      │   │   │
                    │                             │   │   │
                    ▼                             │   │   │
        ┌───────────────────────┐                │   │   │
        │ build/extractor.py    │                │   │   │
        ├───────────────────────┤                │   │   │
        │ RouteExtractor        │                │   │   │
        │  - visit_Assign()     │                │   │   │
        │  - visit_FunctionDef()│                │   │   │
        │                       │                │   │   │
        │ extract_routes()      │                │   │   │
        └───────────────────────┘                │   │   │
                                                 │   │   │
                        ┌────────────────────────┘   │   │
                        │                            │   │
                        ▼                            │   │
            ┌───────────────────────┐               │   │
            │ validator.py          │               │   │
            ├───────────────────────┤               │   │
            │ AppValidator          │               │   │
            │  - validate()         │               │   │
            │  - check signatures   │               │   │
            │  - check types        │               │   │
            │  - check imports      │               │   │
            │                       │               │   │
            │ validate_app()        │               │   │
            │ print_results()       │               │   │
            └───────────────────────┘               │   │
                                                    │   │
                            ┌───────────────────────┘   │
                            │                           │
                            ▼                           │
                ┌───────────────────────┐              │
                │ build/transpiler.py   │              │
                ├───────────────────────┤              │
                │ generate_handler_code()│             │
                │ generate_nucleus_template()         │
                │ generate_codon_server()│             │
                │                       │              │
                │ Creates:              │              │
                │  app_generated.codon  │              │
                └───────────────────────┘              │
                                                       │
                                ┌──────────────────────┘
                                │
                                ▼
                    ┌───────────────────────┐
                    │ build/compiler.py     │
                    ├───────────────────────┤
                    │ check_codon_available()│
                    │ compile_to_binary()   │
                    │                       │
                    │ Runs:                 │
                    │  codon build -o app   │
                    └───────────────────────┘
```

## Data Flow

```
Python Source (app.py)
         │
         ▼
    ┌─────────┐
    │ Extract │  → List[Route]
    └─────────┘      │
         │           ├─ path: "/hello"
         │           ├─ methods: ["GET"]
         │           ├─ handler: "hello"
         │           └─ function: <AST node>
         ▼
    ┌──────────┐
    │ Validate │  → (errors, warnings)
    └──────────┘      │
         │            ├─ Check signatures
         │            ├─ Check types
         │            └─ Check imports
         ▼
    ┌───────────┐
    │ Transpile │  → app_generated.codon
    └───────────┘      │
         │             ├─ Nucleus template
         │             ├─ Handler functions
         │             └─ Route registrations
         ▼
    ┌─────────┐
    │ Compile │  → app (binary)
    └─────────┘
         │
         ▼
    Native Binary
```

## Test Structure

```
tests/
├── run_tests.py          # Master runner
│
└── build/
    ├── test_route_extractor.py
    │   ├── test_single_app_basic
    │   ├── test_different_app_name
    │   ├── test_wrong_app_ignored ★
    │   ├── test_multiple_decorators
    │   ├── test_multiple_routes_same_app
    │   ├── test_no_turbox_app
    │   ├── test_route_without_call
    │   └── test_nested_attribute_ignored ★
    │
    ├── test_transpiler.py
    │   ├── test_simple_string_return
    │   ├── test_nucleus_template_generation
    │   └── test_handler_with_no_return
    │
    └── test_validator.py
        ├── test_valid_handler
        ├── test_missing_type_hints
        ├── test_wrong_return_type
        ├── test_unsupported_imports
        └── test_non_string_return_value

★ = Tests that verify Problem #1 fix
```

## Module Sizes

```
Before Refactoring:
turbox/build.py          400+ lines  ❌ Too large

After Refactoring:
turbox/build.py          ~100 lines  ✅ Main orchestrator
turbox/validator.py      ~260 lines  ✅ Focused module
turbox/build/
  ├─ extractor.py        ~90 lines   ✅ Single responsibility
  ├─ transpiler.py       ~290 lines  ✅ Code generation
  └─ compiler.py         ~50 lines   ✅ Minimal wrapper
```

## Import Graph

```
build.py
  ├─ import validator
  ├─ import build.extractor
  ├─ import build.transpiler
  └─ import build.compiler

build.extractor
  └─ import ast

build.transpiler
  └─ import ast

build.compiler
  └─ import subprocess

validator
  ├─ import ast
  └─ import dataclasses
```

No circular dependencies! ✅

## Usage Example

```python
# Old way (still works)
from turbox.build import build
build("app.py", "my_server")

# New way (for advanced usage)
from turbox.build.extractor import extract_routes
from turbox.build.transpiler import generate_codon_server
from turbox.build.compiler import compile_to_binary
from turbox.validator import validate_app

# Extract
routes = extract_routes("app.py")

# Validate
errors, warnings = validate_app("app.py", source, routes)

# Generate
generate_codon_server(routes, "app.codon")

# Compile
compile_to_binary("app.codon", "app")
```
