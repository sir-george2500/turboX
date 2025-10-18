import socket
from typing import Callable, Dict, Tuple


class TurboX:
    def __init__(self, host: str = "127.0.0.1", port: int = 8000):
        self.host = host
        self.port = port
        self.routes: Dict[Tuple[str, str], Callable] = {}
    
    def route(self, path: str, methods: list[str] | None = None):
        if methods is None:
            methods = ["GET"]
        
        def decorator(func: Callable):
            for method in methods:
                self.routes[(method, path)] = func
            return func
        return decorator
    
    def _parse_request(self, request: bytes) -> Tuple[str, str]:
        lines = request.decode("utf-8").split("\r\n")
        if not lines:
            return "", ""
        
        request_line = lines[0].split()
        if len(request_line) < 3:
            return "", ""
        
        method = request_line[0]
        path = request_line[1]
        
        return method, path
    
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
    
    def _handle_request(self, request: bytes) -> bytes:
        method, path = self._parse_request(request)
        
        if not method or not path:
            return self._build_response("Bad Request", 400)
        
        route_key = (method, path)
        if route_key in self.routes:
            try:
                handler = self.routes[route_key]
                result = handler()
                return self._build_response(str(result), 200)
            except Exception as e:
                return self._build_response(f"Internal Server Error: {str(e)}", 500)
        else:
            return self._build_response("Not Found", 404)
    
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
