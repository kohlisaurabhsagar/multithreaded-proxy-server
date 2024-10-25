import socket
import threading
import logging
from concurrent.futures import ThreadPoolExecutor


PROXY_HOST = '127.0.0.1'
PROXY_PORT = 8888
MAX_THREADS = 10

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def handle_https(client_socket, target_host, target_port):
    try:
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.connect((target_host, target_port))

        client_socket.send(b"Connection Established\r\n\r\n")

        client_socket.setblocking(0)
        server_socket.setblocking(0)

        while True:
            try:
                client_data = client_socket.recv(4096)
                if client_data:
                    server_socket.sendall(client_data)
            except BlockingIOError:
                pass

            try:
                server_data = server_socket.recv(4096)
                if server_data:
                    client_socket.sendall(server_data)
            except BlockingIOError:
                pass
    finally:
        client_socket.close()
        server_socket.close()

def handle_client(client_socket):
    try:
        request = client_socket.recv(4096).decode()
        lines = request.splitlines()
        first_line = lines[0].split()
        method = first_line[0]
        url = first_line[1]
        logging.info(f"Received request: {method} {url}")

        if method == "CONNECT":
            target_host, target_port = url.split(":")
            target_port = int(target_port)
            handle_https(client_socket, target_host, target_port)
            return

        elif method in ["GET", "POST"]:
            if url.startswith("http://"):
                url = url[7:]
            host_end = url.find("/")
            target_host = url[:host_end] if host_end != -1 else url
            target_port = 80

            remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            remote_socket.connect((target_host, target_port))
            remote_socket.send(request.encode())

            while True:
                response = remote_socket.recv(4096)
                if len(response) > 0:
                    client_socket.send(response)
                else:
                    break

            remote_socket.close()

    except Exception as e:
        logging.error(f"Error handling client: {e}")
    finally:
        client_socket.close()

def start_proxy():
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    proxy_socket.bind((PROXY_HOST, PROXY_PORT))
    proxy_socket.listen(10)
    logging.info(f"[*] Proxy server listening on {PROXY_HOST}:{PROXY_PORT}")

    with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
        while True:
            client_socket, addr = proxy_socket.accept()
            logging.info(f"[+] Accepted connection from {addr}")
            executor.submit(handle_client, client_socket)

if __name__ == "__main__":
    start_proxy()
