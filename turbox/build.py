#!/usr/bin/env python3
"""
TurboX Build Tool - Extracts routes from Python and generates Nucleus-based Codon server

The build tool bridges the Python API layer with the Nucleus server core:
1. Parses Python source using AST
2. Extracts route definitions and handler functions
3. Transpiles Python handlers to Codon
4. Generates complete Nucleus server with embedded routes
5. Compiles to native binary using Codon compiler
"""
import ast
import sys
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple


class RouteExtractor(ast.NodeVisitor):
    def __init__(self):
        self.routes: List[Dict] = []
        self.functions: Dict[str, ast.FunctionDef] = {}
        self.app_name = None
    
    def visit_Assign(self, node):
        # Find app = TurboX()
        if isinstance(node.value, ast.Call):
            if isinstance(node.value.func, ast.Name) and node.value.func.id == 'TurboX':
                if node.targets and isinstance(node.targets[0], ast.Name):
                    self.app_name = node.targets[0].id
        self.generic_visit(node)
    
    def visit_FunctionDef(self, node):
        # Store all function definitions
        self.functions[node.name] = node
        
        # Check for @app.route decorator
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Attribute):
                    if decorator.func.attr == 'route':
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
                                    methods = [elt.value for elt in keyword.value if isinstance(elt, ast.Constant)]
                        
                        if path:
                            self.routes.append({
                                'path': path,
                                'methods': methods,
                                'handler': node.name,
                                'function': node
                            })
        
        self.generic_visit(node)


def extract_routes(python_file: str) -> List[Dict]:
    """Extract routes from a Python file"""
    with open(python_file, 'r') as f:
        tree = ast.parse(f.read())
    
    extractor = RouteExtractor()
    extractor.visit(tree)
    
    return extractor.routes


def generate_handler_code(route: Dict) -> str:
    """Generate Codon handler code for a route"""
    func = route['function']
    handler_name = route['handler']
    
    # Simple transpilation: extract return statements
    # For now, handle simple cases
    body_lines = []
    
    for node in func.body:
        if isinstance(node, ast.Return):
            if isinstance(node.value, ast.Constant):
                # Simple string return
                return_value = node.value.value
                body_lines.append(f"    return \"{return_value}\"")
            elif isinstance(node.value, ast.JoinedStr):
                # f-string
                parts = []
                for val in node.value.values:
                    if isinstance(val, ast.Constant):
                        parts.append(val.value)
                    elif isinstance(val, ast.FormattedValue):
                        # Extract the variable/expression
                        if isinstance(val.value, ast.Attribute):
                            # request.query_params.get('name', 'default')[0]
                            parts.append("{...}")  # Placeholder for now
                        elif isinstance(val.value, ast.Name):
                            parts.append(f"{{{val.value.id}}}")
                # For now, generate simple code
                body_lines.append(f"    return \"{''.join(str(p) for p in parts)}\"")
    
    if not body_lines:
        body_lines.append(f"    return \"Response from {handler_name}\"")
    
    return f"""
def {handler_name}(request: Request) -> str:
{chr(10).join(body_lines)}
"""


def generate_codon_server(routes: List[Dict], output_file: str):
    """Generate a complete Nucleus server with embedded routes"""
    
    handler_code = []
    route_registrations = []
    
    for route in routes:
        # Generate handler function
        handler_code.append(generate_handler_code(route))
        
        # Generate route registration
        for method in route['methods']:
            route_registrations.append(
                f"app.routes['{method}:{route['path']}'] = {route['handler']}"
            )
    
    codon_code = f"""# Auto-generated TurboX Nucleus server
# Generated from Python routes - compiled to native code
from C import (
    socket(i32, i32, i32) -> i32,
    setsockopt(i32, i32, i32, Ptr[byte], u32) -> i32,
    bind(i32, Ptr[byte], u32) -> i32,
    listen(i32, i32) -> i32,
    accept(i32, Ptr[byte], Ptr[u32]) -> i32,
    recv(i32, Ptr[byte], int, i32) -> int,
    send(i32, Ptr[byte], int, i32) -> int,
    close(i32) -> i32,
    htons(u16) -> u16,
    inet_addr(Ptr[byte]) -> u32,
    perror(Ptr[byte])
)

# Socket constants
AF_INET = i32(2)
SOCK_STREAM = i32(1)
SOL_SOCKET = i32(1)
SO_REUSEADDR = i32(2)

@tuple
class sockaddr_in:
    sin_family: i16
    sin_port: u16
    sin_addr: u32
    sin_zero: u64

class Request:
    method: str
    path: str
    query_params: Dict[str, str]
    headers: Dict[str, str]
    body: str
    
    def __init__(self, method: str, path: str, query_params: Dict[str, str], 
                 headers: Dict[str, str], body: str):
        self.method = method
        self.path = path
        self.query_params = query_params
        self.headers = headers
        self.body = body

def parse_query_string(query: str) -> Dict[str, str]:
    params = Dict[str, str]()
    if not query:
        return params
    
    pairs = query.split('&')
    for pair in pairs:
        if '=' in pair:
            parts = pair.split('=', 1)
            params[parts[0]] = parts[1]
    return params

def parse_request(request_data: str) -> Request:
    lines = request_data.split('\\r\\n')
    
    # Parse request line
    request_line = lines[0].split(' ')
    method = request_line[0]
    full_path = request_line[1]
    
    # Parse path and query params
    path = full_path
    query_params = Dict[str, str]()
    
    if '?' in full_path:
        parts = full_path.split('?', 1)
        path = parts[0]
        query_params = parse_query_string(parts[1])
    
    # Parse headers
    headers = Dict[str, str]()
    body_start = 0
    
    for i in range(1, len(lines)):
        line = lines[i]
        if line == '':
            body_start = i + 1
            break
        if ': ' in line:
            parts = line.split(': ', 1)
            headers[parts[0].lower()] = parts[1]
    
    # Extract body
    body = ''
    if body_start < len(lines):
        body_lines = lines[body_start:]
        body = '\\r\\n'.join(body_lines)
    
    return Request(method, path, query_params, headers, body)

def build_response(body: str, status: int = 200) -> str:
    status_msg = 'OK'
    if status == 404:
        status_msg = 'Not Found'
    elif status == 500:
        status_msg = 'Internal Server Error'
    elif status == 400:
        status_msg = 'Bad Request'
    
    response = f'HTTP/1.1 {{status}} {{status_msg}}\\r\\n'
    response += 'Content-Type: text/plain\\r\\n'
    response += f'Content-Length: {{len(body)}}\\r\\n'
    response += 'Connection: close\\r\\n'
    response += '\\r\\n'
    response += body
    
    return response

class TurboX:
    host: str
    port: int
    routes: Dict[str, Callable[[Request], str]]
    
    def __init__(self, host: str = '127.0.0.1', port: int = 8000):
        self.host = host
        self.port = port
        self.routes = Dict[str, Callable[[Request], str]]()
    
    def handle_request(self, request_data: str) -> str:
        try:
            req = parse_request(request_data)
            route_key = f'{{req.method}}:{{req.path}}'
            
            if route_key in self.routes:
                handler = self.routes[route_key]
                result = handler(req)
                return build_response(result, 200)
            else:
                return build_response('Not Found', 404)
        except:
            return build_response('Internal Server Error', 500)
    
    def run(self):
        # Create socket
        sockfd = socket(AF_INET, SOCK_STREAM, i32(0))
        if sockfd < i32(0):
            perror('socket'.c_str())
            return
        
        # Enable SO_REUSEADDR
        optval = i32(1)
        setsockopt(sockfd, SOL_SOCKET, SO_REUSEADDR, Ptr[byte](__ptr__(optval)), u32(4))
        
        # Bind
        addr = sockaddr_in(
            i16(AF_INET),
            htons(u16(self.port)),
            inet_addr(self.host.c_str()),
            u64(0)
        )
        
        if bind(sockfd, Ptr[byte](__ptr__(addr)), u32(16)) < i32(0):
            perror('bind'.c_str())
            close(sockfd)
            return
        
        # Listen
        if listen(sockfd, i32(5)) < i32(0):
            perror('listen'.c_str())
            close(sockfd)
            return
        
        print(f'TurboX server running on http://{{self.host}}:{{self.port}}')
        print('Press Ctrl+C to stop')
        
        buffer = Ptr[byte](4096)
        addr_len = u32(16)
        
        while True:
            client_fd = accept(sockfd, cobj(), Ptr[u32](__ptr__(addr_len)))
            
            if client_fd < i32(0):
                continue
            
            # Receive request
            bytes_received = recv(client_fd, buffer, 4096, i32(0))
            
            if bytes_received > 0:
                request_str = str(buffer, bytes_received)
                response = self.handle_request(request_str)
                send(client_fd, response.ptr, len(response), i32(0))
            
            close(client_fd)
        
        close(sockfd)

# Generated handler functions
{''.join(handler_code)}

# Application setup
app = TurboX()

# Register routes
{chr(10).join(route_registrations)}

# Run server
app.run()
"""
    
    with open(output_file, 'w') as f:
        f.write(codon_code)
    
    print(f"Generated Nucleus server: {output_file}")


def build(python_file: str, output_binary: str = None):
    """Build a TurboX app to native binary"""
    
    if not Path(python_file).exists():
        print(f"Error: File {python_file} not found")
        sys.exit(1)
    
    # Extract routes
    print(f"Extracting routes from {python_file}...")
    routes = extract_routes(python_file)
    
    print(f"Found {len(routes)} route(s):")
    for route in routes:
        methods_str = ', '.join(route['methods'])
        print(f"  [{methods_str}] {route['path']} -> {route['handler']}")
    
    # Generate Codon server
    generated_file = python_file.replace('.py', '_generated.codon')
    generate_codon_server(routes, generated_file)
    
    # Compile with Codon
    if output_binary is None:
        output_binary = python_file.replace('.py', '')
    
    print(f"\nCompiling with Codon...")
    result = subprocess.run(
        ['codon', 'build', '-o', output_binary, generated_file],
        capture_output=True,
        text=True
    )
    
    if result.returncode == 0:
        print(f"✅ Successfully built: {output_binary}")
        print(f"\nRun your server: ./{output_binary}")
    else:
        print(f"❌ Compilation failed:")
        print(result.stderr)
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python -m turbox.build <app.py> [output_binary]")
        sys.exit(1)
    
    python_file = sys.argv[1]
    output_binary = sys.argv[2] if len(sys.argv) > 2 else None
    
    build(python_file, output_binary)
