import webapp
from urllib import request, error


class cache(webapp.app):

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

    def process(self, method, parsedRequest, firstRequest):
        if method == 'GET':
            if parsedRequest in webapp.webapp.cacheDic:
                print("LO TENIA \n\n\n")
                return("200 OK", webapp.webapp.cacheDic[parsedRequest])
            else:
                url = "http:/" + parsedRequest
                try:
                    toReturn = request.urlopen(url).read()
                    toReturnStr = toReturn.decode('utf-8', 'ignore')
                    toReturn = self.putUrls(parsedRequest, toReturnStr)
                    webapp.webapp.cacheDic[parsedRequest] = toReturn
                    webapp.webapp.httpSendDic[parsedRequest] = bytes(firstRequest + "/br>", 'utf-8') + toReturn
                    return("200 OK", toReturn)
                except error.URLError:
                    return("400 Bad Request", bytes("URL PEDIDA NO EXISTE:</br><a href=/> Volver a raiz</a>", 'utf-8'))
        return("404 Not Found", bytes("Solo se puede pedir GET", 'utf-8'))


class httpSend(webapp.app):

    def process(self, method, parsedRequest, request):
        if parsedRequest in webapp.webapp.httpSendDic:
            print("\n\nEntra\n\n")
            return ("200 OK", webapp.webapp.httpSendDic[parsedRequest])
        return("404 Not Found", bytes("No se ha pedido esa pagina aun", 'utf-8'))


class httpRec(webapp.app):

    def process(self, method, parsedRequest, request):
        if parsedRequest in webapp.webapp.httpRecDic:
            return ("200 OK", webapp.webapp.httpRecDic[parsedRequest])
        return("404 Not Found", bytes("No se ha pedido esa pagina aun", 'utf-8'))
