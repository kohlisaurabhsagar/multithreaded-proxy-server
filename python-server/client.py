import socket

def demo_client():
    proxy_host = '127.0.0.1'
    proxy_port = 8888
    target_host = "example.com"
    target_path = "/"
    request = f"GET http://{target_host}{target_path} HTTP/1.1\r\n"
    request += f"Host: {target_host}\r\n"
    request += "Connection: close\r\n\r\n"

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        client_socket.connect((proxy_host, proxy_port))
        client_socket.sendall(request.encode())

        response = b""
        while True:
            data = client_socket.recv(4096)
            if not data:
                break
            response += data

    print("Response from the server:")
    print(response.decode(errors="ignore"))

if __name__ == "__main__":
    demo_client()
