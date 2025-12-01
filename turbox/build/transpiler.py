#!/usr/bin/env python3
"""
Code Transpiler - Generates Codon code from Python routes

UPDATED: Now imports from nucleus module instead of embedding template!

Responsible for:
- Transpiling Python handler functions to Codon
- Generating minimal glue code (imports + route registration)
- Using nucleus module for server core
"""
import ast
from typing import List, Dict


def generate_handler_code(route: Dict) -> str:
    """Generate Codon handler code for a route
    
    Args:
        route: Route dictionary with 'function' and 'handler' keys
        
    Returns:
        Codon function code as string
    """
    func = route['function']
    handler_name = route['handler']
    
    # Simple transpilation: extract return statements
    # TODO: Use ast.unparse() for better source preservation (Problem #5)
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


def generate_codon_server_modular(routes: List[Dict], output_file: str):
    """Generate a Codon server using nucleus module
    
    This reads the nucleus module code from turbox/nucleus/__init__.codon
    and includes it in the generated file. This approach:
    - Keeps nucleus code separate and maintainable
    - Avoids Codon import complexity
    - Enables nucleus to be tested independently
    
    Args:
        routes: List of route dictionaries
        output_file: Path to output .codon file
    """
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
    
    # Read nucleus code from the nucleus module
    import os
    from pathlib import Path
    
    turbox_dir = Path(__file__).parent.parent
    nucleus_file = turbox_dir / 'nucleus' / '__init__.codon'
    
    with open(nucleus_file, 'r') as f:
        nucleus_code = f.read()
    
    # Build server code with nucleus included
    codon_code = f"""# Auto-generated TurboX application
# Generated from Python routes - compiled to native code
# Uses modular Nucleus (included from turbox/nucleus/__init__.codon)

# ========== Nucleus Server Core (from turbox/nucleus/__init__.codon) ==========
{nucleus_code}

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
    
    print(f"✨ Generated modular server: {output_file}")
    print(f"   Using nucleus from: {nucleus_file}")


# Keep old function for backward compatibility during transition
def generate_nucleus_template() -> str:
    """Generate the Nucleus server template
    
    DEPRECATED: Use generate_codon_server_modular() instead
    
    This embeds the full server code as a template.
    Kept for backward compatibility during transition.
    
    Returns:
        Nucleus server template code
    """
    return """# Auto-generated TurboX Nucleus server
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
    lines = request_data.split('\\\\r\\\\n')
    
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
        body = '\\\\r\\\\n'.join(body_lines)
    
    return Request(method, path, query_params, headers, body)

def build_response(body: str, status: int = 200) -> str:
    status_msg = 'OK'
    if status == 404:
        status_msg = 'Not Found'
    elif status == 500:
        status_msg = 'Internal Server Error'
    elif status == 400:
        status_msg = 'Bad Request'
    
    response = f'HTTP/1.1 {{status}} {{status_msg}}\\\\r\\\\n'
    response += 'Content-Type: text/plain\\\\r\\\\n'
    response += f'Content-Length: {{len(body)}}\\\\r\\\\n'
    response += 'Connection: close\\\\r\\\\n'
    response += '\\\\r\\\\n'
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
"""


def generate_codon_server(routes: List[Dict], output_file: str):
    """Generate a complete Nucleus server with embedded routes
    
    DEPRECATED: Use generate_codon_server_modular() for new approach
    
    This is kept for backward compatibility during transition.
    It embeds the full server template (old approach).
    
    Args:
        routes: List of route dictionaries
        output_file: Path to output .codon file
    """
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
    
    # Build complete server code
    nucleus_template = generate_nucleus_template()
    
    codon_code = nucleus_template + f"""
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
