# TurboX ⚡

A high-performance Python backend framework built on the Codon compiler.

## About

TurboX leverages Codon to compile Python code to machine code, delivering performance comparable to Rust and C++ without the overhead of traditional Python interpreters.

## Prerequisites

- [Codon compiler](https://github.com/exaloop/codon) installed and available in your PATH
- Linux/macOS (Windows support coming soon)

To check if Codon is installed:
```bash
codon --version
```

## Quick Start

### 1. Running the Minimal Server

The minimal server demonstrates TurboX's core capabilities using Codon's C FFI for direct socket access.

**Compile the server:**
```bash
cd examples
codon build minimal_server.codon
```

This creates a native executable (`minimal_server`) with no Python runtime overhead.

**Run the server:**
```bash
./minimal_server
```

You should see:
```
TurboX server running on http://127.0.0.1:8000
Press Ctrl+C to stop
```

**Test it:**
```bash
curl http://127.0.0.1:8000/
# Output: Hello, World!
```

### 2. Direct Execution (without pre-compilation)

You can also run the server directly:
```bash
codon run examples/minimal_server.codon
```

## Project Status

TurboX is in early development. Currently implemented:

- ✅ Minimal HTTP server using C FFI
- ✅ Basic request/response handling
- ✅ Native compilation to machine code

Coming soon:
- 🔄 Request parsing (HTTP methods, paths, headers, query params)
- 🔄 Routing system with decorators
- 🔄 JSON request/response support
- 🔄 Middleware system
- 🔄 Performance benchmarks

## Development

This framework is in active development. Contributions and feedback welcome!
