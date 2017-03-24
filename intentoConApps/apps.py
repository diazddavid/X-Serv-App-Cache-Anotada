import webapp
from urllib import request, error


class cache(webapp.app):


    
    def process(self, method, parsedRequest, firstRequest, dics):
        if method == 'GET':
            if parsedRequest in dics['cache']:
                print("LO TENIA \n\n\n")
                return("200 OK", dics['cache'][parsedRequest])
            else:
                url = "http:/" + parsedRequest
                try:
                    toReturn = request.urlopen(url).read()
                    toReturnStr = toReturn.decode('utf-8', 'ignore')
                    toReturn = self.putUrls(parsedRequest, toReturnStr)
                    dics['cache'][parsedRequest] = toReturn            
                    dics['httpSend'][parsedRequest] = bytes(firstRequest + "/br>", 'utf-8') + toReturn
                    return("200 OK", toReturn)
                except error.URLError:
                    return("400 Bad Request", bytes("URL PEDIDA NO EXISTE:</br><a href=/> Volver a raiz</a>", 'utf-8'))
        return("404 Not Found", bytes("Solo se puede pedir GET", 'utf-8'))


class httpSend(webapp.app):


    def process(self, method, parsedRequest, request, dics):
        print("\n\n\n" + parsedRequest + "\n\n\n")
        if parsedRequest in dics['httpSend']:
            return ("200 OK", dics['httpSend'][parsedRequest])
        return("404 Not Found", bytes("No se ha pedido esa pagina aun", 'utf-8'))


class httpRec(webapp.app):


    def process(self, method, parsedRequest, request, dics):
        if parsedRequest in dics['httpRec']:
            return ("200 OK", dics['httpRec'][parsedRequest])
        return("404 Not Found", bytes("No se ha pedido esa pagina aun", 'utf-8'))
