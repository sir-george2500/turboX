from C import socket(int, int, int) -> int
from C import bind(int, cobj, int) -> int
from C import listen(int, int) -> int
from C import accept(int, cobj, cobj) -> int
from C import recv(int, cobj, int, int) -> int
from C import send(int, cobj, int, int) -> int
from C import close(int) -> int
from C import htons(u16) -> u16
from C import htonl(u32) -> u32

# Socket constants
AF_INET = 2
SOCK_STREAM = 1
SOL_SOCKET = 1
SO_REUSEADDR = 2

@tuple
class sockaddr_in:
    sin_family: u16
    sin_port: u16
    sin_addr: u32
    sin_zero: Ptr[byte]

def create_server(host: str, port: int) -> int:
    sockfd = socket(AF_INET, SOCK_STREAM, 0)
    if sockfd < 0:
        print("Error creating socket")
        return -1
    
    # Parse IP address (simple 127.0.0.1 case)
    addr = sockaddr_in(
        u16(AF_INET),
        htons(u16(port)),
        htonl(u32(0x7F000001)),  # 127.0.0.1
        Ptr[byte]()
    )
    
    if bind(sockfd, __ptr__(addr).as_byte(), 16) < 0:
        print("Error binding socket")
        close(sockfd)
        return -1
    
    if listen(sockfd, 5) < 0:
        print("Error listening on socket")
        close(sockfd)
        return -1
    
    return sockfd

def main():
    sockfd = create_server("127.0.0.1", 8000)
    if sockfd < 0:
        return
    
    print("Server listening on http://127.0.0.1:8000")
    
    response = b"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nContent-Length: 13\r\n\r\nHello, World!"
    
    while True:
        client_addr = sockaddr_in()
        addr_len = 16
        
        client_fd = accept(sockfd, __ptr__(client_addr).as_byte(), __ptr__(addr_len))
        if client_fd < 0:
            continue
        
        buffer = array[byte](4096)
        recv(client_fd, __ptr__(buffer[0]).as_byte(), 4096, 0)
        
        send(client_fd, __ptr__(response[0]).as_byte(), len(response), 0)
        close(client_fd)

main()
