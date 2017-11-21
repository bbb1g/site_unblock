# -*- coding: utf8 -*-
import time
from socket import *
from select import *
from multiprocessing import Process

import requests


def get_fake_request():
    return """GET /dhafiosdfhasodufhasdiuyfgaisudyf HTTP/1.1
Host: cykorr.krr"""


def handle_proxy(data, fd):
    print data
    try:
        request, headers = data.split('\n', 1)
    except ValueError:
        return

    method, url, protocol = request.split(' ')
    schema, host = url.split('://')

    print repr(method)
    if method != 'GET':
        request = getattr(requests, method.lower(), None)
        if request is None:
            return
        try:
            r = request(url)
        except Exception:
            return
        return fd.send(r.content)

    req = get_fake_request() + '\n\n' + data

    proxy_sock = socket(AF_INET, SOCK_STREAM)
    proxy_sock.connect((host.strip('/'), 80))
    proxy_sock.send(req)

    res = receive_all(proxy_sock)
    ok_idx = res.find('200 OK\r\n') - 9
    print res[ok_idx:]
    fd.send(res[ok_idx:])


def receive_all(s):
    data = ''
    while True:
        rc = s.recv(1024)
        if not rc:
            break
        data += rc
    return data


socks = []
server = socket(AF_INET, SOCK_STREAM)
server.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server.bind(('127.0.0.1', 8080))
server.listen(10)
socks.append(server)

while True:
    try:
        read_fds, write_fds, except_fds = select(socks, [], [])
    except KeyboardInterrupt:
        break

    for read_fd in read_fds:#zip(read_fds, write_fds):
        if read_fd == server:
            client, _ = server.accept()
            socks.append(client)
        else:
            data = receive_all(read_fd)
            if data:
                print data
                Process(target=handle_proxy, args=(data, read_fd)).start()
            else:
                read_fd.close()
                #write_fd.close()
                socks.remove(read_fd)
                #socks.remove(write_fd)
    time.sleep(0.5)

server.close()
