# TurboX Build System Architecture

## Overview

TurboX uses a **two-tier architecture** similar to FastAPI + Uvicorn:

1. **Python Layer** (`turbox/app.py`) - Developer-friendly routing API
2. **Codon Layer** (`minimal_server.codon`) - High-performance C FFI socket server

## How It Works

### Development Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Developer writes app.py using Python API                   │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  from turbox import TurboX                            │  │
│  │                                                        │  │
│  │  app = TurboX()                                       │  │
│  │                                                        │  │
│  │  @app.route("/")                                      │  │
│  │  def hello(request):                                  │  │
│  │      return "Hello, World!"                           │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ turbox build app.py
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Build Tool (turbox/build.py)                               │
│  1. Parse Python AST                                        │
│  2. Extract routes and handlers                            │
│  3. Transpile function bodies                              │
│  4. Generate Codon source code                             │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ generates
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  app_generated.codon                                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  # C FFI socket code                                  │  │
│  │  from C import socket, bind, listen...                │  │
│  │                                                        │  │
│  │  # Generated handler functions                        │  │
│  │  def hello(request: Request) -> str:                  │  │
│  │      return "Hello, World!"                           │  │
│  │                                                        │  │
│  │  # Route registration                                 │  │
│  │  app = TurboX()                                       │  │
│  │  app.routes['GET:/'] = hello                          │  │
│  │  app.run()                                            │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                           │
                           │ codon build
                           ▼
┌─────────────────────────────────────────────────────────────┐
│  Native Binary (~200KB)                                     │
│  • No Python runtime needed                                │
│  • C-level performance                                     │
│  • Direct system calls via FFI                             │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Python API Layer (`turbox/app.py`)

**Purpose**: Provide familiar Flask/FastAPI-like API for developers

**Features**:
- Decorator-based routing (`@app.route()`)
- Request object with parsed data
- Query params, headers, body parsing
- JSON and form data support

**Used for**: Development and testing (runs with Python interpreter)

### 2. Build Tool (`turbox/build.py`)

**Purpose**: Bridge between Python and Codon

**Process**:
1. **Parse**: Use Python AST to analyze source code
2. **Extract**: Find all routes and handler functions
3. **Transpile**: Convert Python function bodies to Codon syntax
4. **Generate**: Create complete Codon server with embedded handlers
5. **Compile**: Invoke Codon compiler to produce native binary

**Key Features**:
- AST-based route extraction
- Function body transpilation
- Automatic route registration
- Error handling and validation

### 3. Nucleus Server (Codon Core)

**Purpose**: High-performance HTTP server using C FFI

**Features**:
- Direct socket operations via C FFI
- Zero-copy where possible
- Minimal overhead
- HTTP request parsing
- Route matching and dispatch

**Components**:
- Socket creation and management
- HTTP request parser
- Route dispatcher
- Response builder

## Build Commands

### CLI Tool (`turbox/cli.py`)

```bash
# Build to native binary
turbox build app.py [output_name]

# Build and run
turbox run app.py
```

### What Happens

1. **Parse Python file**: Extract routes using AST
2. **Generate Codon code**: Create `app_generated.codon`
3. **Compile**: Run `codon build -o binary app_generated.codon`
4. **Output**: Native executable ready to deploy

## Current Capabilities

### ✅ Implemented

- Basic route extraction
- GET request routing
- Simple return value transpilation
- Query parameter parsing
- Header parsing
- Request/Response handling
- Native binary compilation

### 🔄 In Progress

- Complex Python expression transpilation
- POST body parsing in Codon
- JSON request/response
- Form data handling

### 🎯 Future

- Middleware system
- WebSocket support
- Template rendering
- Static file serving
- Async/concurrent request handling
- Path parameters (e.g., `/user/{id}`)

## Example Workflow

### Step 1: Write Python App

```python
# app.py
from turbox import TurboX

app = TurboX()

@app.route("/")
def index(request):
    return "Hello, World!"

@app.route("/user")
def user(request):
    name = request.query_params.get('name', ['Guest'])[0]
    return f"Hello, {name}!"
```

### Step 2: Build

```bash
turbox build app.py my_server
```

Output:
```
Extracting routes from app.py...
Found 2 route(s):
  [GET] / -> index
  [GET] /user -> user
Generated Codon server: app_generated.codon
Compiling with Codon...
✅ Successfully built: my_server
```

### Step 3: Deploy

```bash
./my_server
```

The binary:
- Contains all routes compiled in
- No Python runtime needed
- ~200KB size
- Fast startup (<10ms)
- C-level performance

## Architecture Benefits

### FastAPI/Uvicorn Model

- **FastAPI**: Python framework, developer-friendly API
- **Uvicorn**: Async ASGI server, handles I/O efficiently

### TurboX Model

- **turbox/app.py**: Python framework, familiar API
- **Nucleus (Codon)**: Compiled C FFI server, native performance

### Key Advantage

Unlike FastAPI+Uvicorn which still runs on Python:
- TurboX compiles **everything** to native code via Nucleus
- No interpreter overhead
- No GIL limitations
- True zero-copy operations possible
- Deploy single binary (no dependencies)

## Technical Details

### Route Registration

Generated Codon code:
```python
app = TurboX()
app.routes['GET:/'] = handler_function
app.routes['POST:/api/data'] = api_handler
```

### Request Dispatch

```python
def handle_request(self, request_data: str) -> str:
    req = parse_request(request_data)
    route_key = f'{req.method}:{req.path}'
    
    if route_key in self.routes:
        handler = self.routes[route_key]
        result = handler(req)
        return build_response(result, 200)
    else:
        return build_response('Not Found', 404)
```

### Performance Path

```
Network → Socket (C FFI) → Parse Request (Codon) → 
Route Dispatch (Dict lookup) → Handler (Compiled) → 
Build Response (Codon) → Send (C FFI) → Network
```

Everything runs in compiled native code with no interpreter overhead.
