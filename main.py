import datetime
import os
import socket


def create_serv(port):
    server = socket.create_server(('', port))
    server.listen()
    return server


def accept_client_conn(serv, cid):
    client_sock, _ = serv.accept()
    print(f'Client #{cid} connected')
    return client_sock


def serve_client(client_sock, cid):
    child_pid = os.fork()
    if child_pid:
        client_sock.close()
        return child_pid

    data = client_sock.recv(1024).decode('utf-8')

    content = load_pade(data)
    client_sock.send(content)
    client_sock.shutdown(socket.SHUT_RDWR)


def load_pade(data):
    split = data.split(' ')

    path = split[1]
    if path[len(path) - 1] == '/':
        path += 'index.html'

    method = split[0]
    _, extension = os.path.splitext(path)
    res_len = 0

    try:
        if method == 'GET':
            with open('./httptest' + path, 'rb') as file:
                res = file.read()
            res_len = len(res)
        else:
            res_len = os.path.getsize('./httptest' + path)

        return create_http_response(200, extension, res_len).encode('utf-8') + res
    except FileNotFoundError:
        return create_http_response(404, 'text/html', res_len).encode('utf-8')


def create_http_response(status, c_type, c_len):
    return f'HTTP/1.1 {status}\r\nContent-Type: {c_type}\r\nContent-Length: {c_len}\r\nServer: Aleksey/2.0\r\nDate: {datetime.datetime.now()}\r\nConnection: close\r\n\r\n'


def reap_children(active_children):
    for child_pid in active_children.copy():
        child_pid, _ = os.waitpid(child_pid, os.WNOHANG)
        if child_pid:
            active_children.discard(child_pid)


def run_server(port=5050):
    serv_sock = create_serv(port)
    active_children = set()
    cid = 0

    while True:
        client_sock = accept_client_conn(serv_sock, cid)
        client_pid = serve_client(client_sock, cid)
        active_children.add(client_pid)

        if cid != 0 and cid % 50 == 0:
            # close child process
            reap_children(active_children)

        cid += 1


run_server()