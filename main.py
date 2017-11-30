import SocketServer
import socket

def getHost(data):

    hostIdx = data.find("Host: ")
    if hostIdx == -1:
        return 0
    host = data[hostIdx:].split("\r\n",1)[0]
    return host[6:]


def ru(s, v):
    t = ''
    while True:
        m = s.recv(1)
        if len(m) == 0:
            return 0
        t += m
        if v in t:
            return t


def getContentLength(data):
    idx = data.find("Content-Length")
    if idx == -1:
        idx2 = data.find("Transfer-Encoding: chunked")
        if idx2 == -1:
            return -1
        else:
            return -2
    return int(data[idx+16:].split("\r\n",1)[0])


def rn(s, n):
    b=""
    while len(b) < n:
        b += s.recv(1)

    return b


def rc(s, header):
    cl = getContentLength(header)
    if cl == -2:
        res = ""
        while True:
            cl = ru(s, '\r\n\r\n')[:-4]
            print "CL1: "+repr(cl)
            cl = int(cl, 16)
            print "CL2: "+hex(cl)
            if cl == 0:
                return res
            res += rn(s, cl)
            print "NOW: "+repr(res)
    elif cl == -1:
        return ""
    else:
        return rn(s, cl)


fakePayload = "Get http://google.com/ HTTP/1.1\r\nHost: google.com\r\n\r\n"


class MyTCPHandler(SocketServer.BaseRequestHandler):

    def handle(self):

        data = ru(self.request, '\r\n\r\n')
        if data == 0:
            print "Something Wrong!!"
            return

        print data
        host = getHost(data)
        if not host:
            print "Something Wrong!!"
            return

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print "Connecting %s:%d" % (host, 80)
        s.connect((host, 80))
        s.send(fakePayload + data)

        print "GOOD"

        firstHeader = ru(s, '\r\n\r\n')
        print "First Header: "+repr(firstHeader)
        content = rc(s, firstHeader)
        print "First Content: "+repr(content)
        secondHeader = ru(s, '\r\n\r\n')
        print "Second Header: "+repr(secondHeader)
        content = rc(s, secondHeader)
        print "Second Content: "+repr(content)

        # rn(s, cl)
        #
        # res = ru(s, '\r\n\r\n')
        # print repr(res)
        # cl = getContentLength(res)
        # if cl == -2:
        #     tmp = ru(s, '\r\n\r\n\r\n')
        #     repr(tmp)
        #     cl = int(tmp[:-3], 16)
        # elif cl == -1:
        #     cl = 0
        # res += rn(s, cl)
        #
        # print repr(res)
        self.request.sendall(secondHeader + content)

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    # Create the server, binding to localhost on port 9999
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
