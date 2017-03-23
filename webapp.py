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
        toReturn = "<p> Tengo en cache: </p>"
        for url in webapp.cacheDic.keys():
            toReturn = toReturn + "<p>" + url + "</p>"
        return toReturn

    def process(self, method, parsedRequest, request):
        """Process the relevant elements of the request.
        Returns the HTTP code for the reply, and an HTML page.
        """

        return ("200 OK", bytes("<html><body><h1>" +
                          "Bienvenido, en cache tengo: </h1> "
                          + self.printDic() + "</body></html>", 'utf-8'))

import apps


class webapp:
    """Root of a hierarchy of classes implementing web applications
    This class does almost nothing. Usually, new classes will
    inherit from it, and by redefining "parse" and "process" methods
    will implement the logic of a web application in particular.
    """

    httpSendDic = {}
    cacheDic = {}
    httpRecDic = {}

    def select(self, parsedRequest):

        if parsedRequest == "/" :
            print("Running app for / \n")
            return (self.default, parsedRequest)
        for prefix in self.apps.keys():
            if  parsedRequest.startswith(prefix):
                print("Running app for prefix: " + prefix + "\n")
                print(prefix)
                parsedRequest = parsedRequest[:parsedRequest.find("/")]
                return (self.apps[prefix], parsedRequest)
        else:
            print("Runing app cache\n")
            return (self.apps['cache'], parsedRequest)

    def __init__(self, hostname, port, apps):
        """Initialize the web application."""

        # Create a TCP objet socket and bind it to a port
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mySocket.bind((hostname, port))

        # Queue a maximum of 5 TCP connection requests
        mySocket.listen(5)

        self.apps = apps
        self.default = app()

        # Accept connections, read incoming data, and call
        # parse and process methods (in a loop)

        while True:
            print('Waiting for connections')
            (recvSocket, address) = mySocket.accept()
            print('HTTP request received (going to parse and process):')
            request = recvSocket.recv(2048).decode('utf-8', 'ignore')
            print(request)
            (method, parsedRequest) = self.default.parse(request)
            (theApp, parsedRequest) = self.select(parsedRequest)
            (returnCode, htmlAnswer) = theApp.process(method, parsedRequest, request)
            print('Answering back...')
            toReturn = bytes(request, 'utf-8')
            toReturn += bytes("HTTP/1.1 " + returnCode + " \r\n\r\n", 'utf-8') + htmlAnswer + bytes("\r\n", 'utf-8')
            recvSocket.send(bytes("HTTP/1.1 " + returnCode + " \r\n\r\n", 'utf-8') + htmlAnswer + bytes("\r\n", 'utf-8'))
            recvSocket.close()

if __name__ == "__main__":
    cache = apps.cache()
    httpSend = apps.httpSend()
    httpRec = apps.httpRec()
    testWebApp = webapp("localhost", 1234, {'cache': cache,
                                            '/httpRec': httpRec,
                                            '/httpSend': httpSend})
