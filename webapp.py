#!/usr/bin/python3

"""
webAppMulti class
Root for hierarchy of classes implementing web applications
Each class can dispatch to serveral web applications, depending
on the prefix of the resource name
Copyright Jesus M. Gonzalez-Barahona, Gregorio Robles (2009-15)
jgb @ gsyc.es
TSAI, SAT and SARO subjects (Universidad Rey Juan Carlos)
October 2009, February 2015
"""

import socket
from urllib import request, error

class app:

    def parse(self, request):
        """Parse the received request, extracting the relevant information.
        request: HTTP request received from the client
        """

        return (request.split(' ', 2)[0], request.split(' ', 2)[1])

    def printDic(self):
        to_return = "<p> Tengo en cache: </p>"
        for url in webApp.cacheDic.keys():
            to_return = to_return + "<p>" + url + "</p>"
        return to_return

    def process(self, method, parsedRequest):
        """Process the relevant elements of the request.
        Returns the HTTP code for the reply, and an HTML page.
        """

        return ("200 OK", bytes("<html><body><h1>" +
                          "Bienvenido, en cache tengo: </h1> "
                          + self.printDic() + "</body></html>", 'utf-8'))

class cache(app):

    def process(self, method, parsedRequest):
        if method == 'GET':
            if parsedRequest in webApp.cacheDic:
                try:
                    return("200 OK", webApp.cacheDic[parsedRequest].read())
                except error.URLError:
                    return("400 Bad Request", bytes("Fav.ico", 'utf-8'))
            else:
                url = "http:/" + parsedRequest
                try:
                    webApp.cacheDic[parsedRequest] = request.urlopen(url)
                    to_return = webApp.cacheDic[parsedRequest].read()
                    return("200 OK", to_return)
                except error.URLError:
                    return("400 Bad Request", bytes("Fav.ico", 'utf-8'))
        return("404 Not Found", bytes("Solo se puede pedir GET", 'utf-8'))


class webApp:
    """Root of a hierarchy of classes implementing web applications
    This class does almost nothing. Usually, new classes will
    inherit from it, and by redefining "parse" and "process" methods
    will implement the logic of a web application in particular.
    """

    cacheDic = {}

    def __init__(self, hostname, port):
        """Initialize the web application."""

        # Create a TCP objet socket and bind it to a port
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mySocket.bind((hostname, port))

        self.default = app()
        self.cache = cache()

        # Queue a maximum of 5 TCP connection requests
        mySocket.listen(5)

        # Accept connections, read incoming data, and call
        # parse and process methods (in a loop)

        while True:
            print('Waiting for connections')
            (recvSocket, address) = mySocket.accept()
            print('HTTP request received (going to parse and process):')
            request = recvSocket.recv(2048).decode('utf-8')
            print(request)
            (method, parsedRequest) = self.default.parse(request)
            if parsedRequest == "/" :
                (returnCode, htmlAnswer) = self.default.process(method, parsedRequest)
            else:
                (returnCode, htmlAnswer) = self.cache.process(method, parsedRequest)
            print('Answering back...')
            recvSocket.send(bytes("HTTP/1.1 " + returnCode + " \r\n\r\n", 'utf-8')
                            + htmlAnswer + bytes("\r\n", 'utf-8'))
            recvSocket.close()

if __name__ == "__main__":
    testWebApp = webApp("localhost", 1234)
