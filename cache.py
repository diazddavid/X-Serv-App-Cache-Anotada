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


    def parse(self, request, dic):
        """Parse the received request, extracting the relevant information.
        request: HTTP request received from the client
        """
        
        parsedRequest = request.split(' ', 2)[1]
        if parsedRequest == "/" :
            print("Running app for / \n")
            mode = "root"
            return (request.split(' ', 2)[0], parsedRequest, mode)
        for prefix in dic.keys():
            if  parsedRequest[1:].startswith(prefix):
                print("Running app for prefix: " + prefix + "\n")
                mode = prefix   
                parsedRequest = parsedRequest[1:]
                parsedRequest = parsedRequest[parsedRequest.find("/"):]     
                return (request.split(' ', 2)[0], parsedRequest, mode)       
        print("Runing app cache\n")
        mode = "cache"        
        
        return (request.split(' ', 2)[0], parsedRequest, mode)
    
    def putUrls(self, parsedRequest, html):
        bodyIndex = html.find("<body")
        bodyHead = html[bodyIndex:]
        bodyIndexStart = bodyHead.find(">")
        start = html[:bodyIndex + bodyIndexStart + 1]
        end = html[bodyIndex + bodyIndexStart + 1:]
        url1 = "<a href=http:/" + parsedRequest + "> URL Original</a>"
        url2 = "</br><a href=" + parsedRequest + "> Recargar</a>"
        url3 = "</br><a href=/httpRec" + parsedRequest + "> HTTP de la peticion</a>"
        url4 = "</br><a href=/httpSend" + parsedRequest + "> HTTP de la respuesta</a>"
        toReturn = start + url1 + url2 + url3 + url4 + end

        return(bytes(toReturn, 'utf-8'))


    def printDic(self, dic):
        toReturn = "<p> Tengo en cache: </p>"
        for url in dic['cache'].keys():
            toReturn += "<p>" "<a href=" + url + ">"
            toReturn += url + "</a>" + "</p>"             
        
        return toReturn

    def process(self, method, parsedRequest, firstRequest, mode, dic):
        """Process the relevant elements of the request.
        Returns the HTTP code for the reply, and an HTML page.
        """       
        if method == 'GET':
            if mode == "root":
                return ("200 OK", bytes("<html><body><h1>" +
                                 "Bienvenido, en cache tengo: </h1> "
                                 + self.printDic(dic) + "</body></html>", 'utf-8'))

            elif mode == "cache":        
                if parsedRequest in dic['cache']:
                    return("200 OK", dic['cache'][parsedRequest])
                else:
                    url = "http:/" + parsedRequest
                    try:
                        toReturn = request.urlopen(url).read()
                        toReturnStr = toReturn.decode('utf-8', 'ignore')
                        toReturn = self.putUrls(parsedRequest, toReturnStr)
                        dic['cache'][parsedRequest] = toReturn            
                        dic['httpSend'][parsedRequest] = bytes(firstRequest + "/br>", 'utf-8')
                        return("200 OK", toReturn)
                    except error.URLError:
                        return("400 Bad Request", bytes("<html><body><h1>URL PEDIDA NO EXISTE:" 
                                                        + "</br><a href=/> Volver a raiz</a>"
                                                        + "</h1></body></html>", 'utf-8'))
            
            elif mode == "httpSend":
                if parsedRequest in dic['httpSend']:
                    return ("200 OK", dic['httpSend'][parsedRequest])       
                return("404 Not Found", bytes("No se ha pedido esa pagina aun", 'utf-8'))        

            elif mode == "httpRec":
                if parsedRequest in dic['httpRec']:
                    return ("200 OK", dic['httpRec'][parsedRequest])
                return("404 Not Found", bytes("No me queda claro que peticion hay que guardar en este diccionario", 'utf-8'))            

        return("404 Not Found", bytes("Solo se puede pedir GET", 'utf-8'))


class webapp:
    """Root of a hierarchy of classes implementing web applications
    This class does almost nothing. Usually, new classes will
    inherit from it, and by redefining "parse" and "process" methods
    will implement the logic of a web application in particular.
    """

    def __init__(self, hostname, port):
        """Initialize the web application."""

        # Create a TCP objet socket and bind it to a port
        mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mySocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        mySocket.bind((hostname, port))

        # Queue a maximum of 5 TCP connection requests
        mySocket.listen(5)

        self.cacheDic = {}
        self.httpSendDic = {}    
        self.httpRecDic = {}
        self.dic = {'cache': self.cacheDic,
                    'httpSend': self.httpSendDic,
                    'httpRec': self.httpRecDic,}        

        self.app = app()        

        # Accept connections, read incoming data, and call
        # parse and process methods (in a loop)

        while True:
            print('Waiting for connections')
            (recvSocket, address) = mySocket.accept()
            print('HTTP request received (going to parse and process):')
            request = recvSocket.recv(2048).decode('utf-8', 'ignore')
            print(request)
            (method, parsedRequest, mode) = self.app.parse(request, self.dic)
            (returnCode, htmlAnswer) = self.app.process(method, parsedRequest, request, mode, self.dic)
            print('Answering back...')
            toReturn = bytes(request, 'utf-8')
            toReturn += bytes("HTTP/1.1 " + returnCode + " \r\n\r\n", 'utf-8') + htmlAnswer + bytes("\r\n", 'utf-8')
            recvSocket.send(bytes("HTTP/1.1 " + returnCode + " \r\n\r\n", 'utf-8') + htmlAnswer + bytes("\r\n", 'utf-8'))
            recvSocket.close()

if __name__ == "__main__":
    testWebApp = webapp("localhost", 1234)