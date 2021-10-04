import os
import urllib
from datetime import datetime


def reap_children(active_children):
    for child_pid in active_children.copy():
        child_pid, _ = os.waitpid(child_pid, os.WNOHANG)
        if child_pid:
            active_children.discard(child_pid)


def create_http_response(status, c_type, c_len, conn='open'):
    if len(c_type) == 0:
        c_type = 'default'

    status_mes = {
        200: 'OK',
        403: 'Forbidden',
        404: 'NotFound',
        405: 'MethodNotAllowed'
    }

    mimetypes = {
        '.html': "text/html",
        '.css': "text/css",
        '.js': "application/javascript",
        '.jpg': "image/jpeg",
        '.jpeg': "image/jpeg",
        '.png': "image/png",
        '.gif': "image/gif",
        '.swf': "application/x-shockwave-flash",
        '.ico': "image/x-icon",
        '.txt': "text",
        'default': ''
    }

    return f'HTTP/1.1 {status} {status_mes[status]}\r\nContent-Type: {mimetypes[c_type]}\r\nContent-Length: {c_len}\r\nServer: Aleksey/2.0\r\nDate: {datetime.now()}\r\nConnection: {conn}\r\n\r\n'


def valid_path(path):
    path = urllib.parse.unquote(path)
    path = path.split('?')[0]

    if path[len(path) - 1] == '/':
        if len(path.split('.')) < 2:
            path += 'index.html'

    if path.find('/etc/passwd') != -1:
        return ''

    if path.startswith('/httptest') is False:
        path = '/httptest' + path

    return path
