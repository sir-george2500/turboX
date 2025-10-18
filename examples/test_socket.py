import socket

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(("127.0.0.1", 8000))
s.listen(5)

print("Server listening on http://127.0.0.1:8000")

while True:
    conn, addr = s.accept()
    print(f"Connected by {addr}")
    
    request = conn.recv(4096)
    
    response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 13\r\n\r\nHello, World!"
    conn.sendall(response)
    conn.close()
