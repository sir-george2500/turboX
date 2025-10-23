import socket
import json
from typing import Callable, Dict, Tuple, Any, Optional
from urllib.parse import parse_qs, urlparse


class Request:
    def __init__(self, method: str, path: str, query_params: Dict[str, list[str]], 
                 headers: Dict[str, str], body: bytes):
        self.method = method
        self.path = path
        self.query_params = query_params
        self.headers = headers
        self.body = body
        self._json_cache: Optional[Any] = None
    
    def json(self) -> Any:
        if self._json_cache is None:
            if self.body:
                self._json_cache = json.loads(self.body.decode('utf-8'))
            else:
                self._json_cache = None
        return self._json_cache
    
    def form(self) -> Dict[str, list[str]]:
        if self.body:
            return parse_qs(self.body.decode('utf-8'))
        return {}


class TurboX:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self.host = host
        self.port = port
        self.routes: Dict[Tuple[str, str], Callable] = {}
    
    def route(self, path: str, methods: list[str] | None = None):
        """Generic route decorator supporting multiple HTTP methods"""
        if methods is None:
            methods = ["GET"]
        
        def decorator(func: Callable):
            for method in methods:
                self.routes[(method, path)] = func
            return func
        return decorator
    
    def get(self, path: str):
        """Decorator for GET requests"""
        return self.route(path, methods=["GET"])
    
    def post(self, path: str):
        """Decorator for POST requests"""
        return self.route(path, methods=["POST"])
    
    def put(self, path: str):
        """Decorator for PUT requests"""
        return self.route(path, methods=["PUT"])
    
    def delete(self, path: str):
        """Decorator for DELETE requests"""
        return self.route(path, methods=["DELETE"])
    
    def patch(self, path: str):
        """Decorator for PATCH requests"""
        return self.route(path, methods=["PATCH"])
    
    def head(self, path: str):
        """Decorator for HEAD requests"""
        return self.route(path, methods=["HEAD"])
    
    def options(self, path: str):
        """Decorator for OPTIONS requests"""
        return self.route(path, methods=["OPTIONS"])

    def _parse_request(self, request: bytes) -> Optional[Request]:
        try:
            request_str = request.decode("utf-8")
            lines = request_str.split("\r\n")
            
            if not lines:
                return None
            
            request_line = lines[0].split()
            if len(request_line) < 3:
                return None
            
            method = request_line[0]
            full_path = request_line[1]
            
            # Parse path and query parameters
            parsed_url = urlparse(full_path)
            path = parsed_url.path
            query_params = parse_qs(parsed_url.query)
            
            # Parse headers
            headers = {}
            body_start_idx = 0
            for i, line in enumerate(lines[1:], 1):
                if line == "":
                    body_start_idx = i + 1
                    break
                if ": " in line:
                    key, value = line.split(": ", 1)
                    headers[key.lower()] = value
            
            # Extract body
            body = b""
            if body_start_idx < len(lines):
                body_text = "\r\n".join(lines[body_start_idx:])
                body = body_text.encode("utf-8")
            
            return Request(method, path, query_params, headers, body)
        except Exception:
            return None

    # build up the http response  
    def _build_response(self, body: str, status: int = 200) -> bytes:
        status_messages = {
            200: "OK",
            404: "Not Found",
            500: "Internal Server Error"
        }
        
        status_msg = status_messages.get(status, "Unknown")
        response = f"HTTP/1.1 {status} {status_msg}\r\n"
        response += "Content-Type: text/plain\r\n"
        response += f"Content-Length: {len(body)}\r\n"
        response += "Connection: close\r\n"
        response += "\r\n"
        response += body
        
        return response.encode("utf-8")
   
    # handle request I am betting on this to do the Job now 
    def _handle_request(self, request_bytes: bytes) -> bytes:
        req = self._parse_request(request_bytes)
        
        if req is None:
            return self._build_response("Bad Request", 400)
        
        route_key = (req.method, req.path)
        if route_key in self.routes:
            try:
                handler = self.routes[route_key]
                result = handler(req)
                return self._build_response(str(result), 200)
            except Exception as e:
                return self._build_response(f"Internal Server Error: {str(e)}", 500)
        else:
            return self._build_response("Not Found", 404)
     
    # run the server
    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        
        print(f"TurboX server running on http://{self.host}:{self.port}")
        
        try:
            while True:
                client_socket, _ = server_socket.accept()
                
                try:
                    request = client_socket.recv(4096)
                    if request:
                        response = self._handle_request(request)
                        client_socket.sendall(response)
                finally:
                    client_socket.close()
        except KeyboardInterrupt:
            print("\nShutting down server...")
        finally:
            server_socket.close()
