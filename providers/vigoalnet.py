import httplib
import urllib
from core.decoder import Decoder

class Vigoal():

    cookie = ""

    @staticmethod
    def getChannels(page):
        #print "original page: "+page
        #print "original page: "+page
        if str(page) == '0':
            page="http://www.vipgoal.net/"
        html = Vigoal.getContentFromUrl(page)
        x = []
        if page.find(".html")==-1:
            table = Decoder.extract("<center>","</center>",html)
            for fieldHtml in table.split('<a href="'):
                element = {}
                element["link"] = fieldHtml[0:fieldHtml.find('"')]
                element["title"] = fieldHtml[fieldHtml.find('title="')+len('title="'):]
                element["title"] = element["title"][0:element["title"].find('"')]
                element["thumbnail"] = fieldHtml[fieldHtml.find('<img src="')+len('<img src="'):]
                element["thumbnail"] = element["thumbnail"][0:element["thumbnail"].find('"')]
                print "found title: "+element["title"]+", link: "+element["link"]+", thumb: "+element["thumbnail"]
                if element["link"].find("http")==0:
                    x.append(element)
        else:
            x.append(Vigoal.extractChannel(html))
        return x

    @staticmethod
    def extractChannel(html):
        element = {}
        #http://www.playerapp1.pw/channel.php?file=120&width=590&height=400&autostart=true
        if html.find('<script type="text/javascript" src="http://www.playerapp1.pw/channel.php?file=')>-1:
            scriptUrl = Decoder.extractWithRegex('http://www.playerapp1.pw/channel.php?file=','"',html)
            html2 = Vigoal.getContentFromUrl(scriptUrl)
            print html2
            lastUrl = Decoder.extractWithRegex('http://','" ',html2)
            lastUrl = lastUrl.replace('"',"")
            print "last url: "+lastUrl+", cookie="+Vigoal.cookie
            html3 = Vigoal.getContentFromUrl(lastUrl,"",Vigoal.cookie,lastUrl)
            print "last html: "+html3
            playerUrl = Decoder.decodeBussinessApp(html3,lastUrl)
            print "player url is: "+playerUrl
            element["title"] = "Watch streaming"
            element["permalink"] = True
            element["link"] = playerUrl

        return element

    @staticmethod
    def getContentFromUrl(url,data="",cookie="",referer=""):
        form = urllib.urlencode(data)
        host = url[url.find("://")+len("://"):]
        subUrl = ""
        print "url is: "+host
        if host.find("/")>-1:
            host = host[0:host.find("/")]
            subUrl = url[url.find(host)+len(host):]
        print "host: "+host+":80 , subUrl: "+subUrl
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0",
            "Accept-Language" : "en-US,en;q=0.8,es-ES;q=0.5,es;q=0.3",
            #"Accept-Encoding" : "gzip, deflate",
            "Conection" : "keep-alive",
            "Host":host,
            "DNT":"1",
            #"Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Host":host
        }
        if referer!="":
            headers["Referer"] = referer

        h = httplib.HTTPConnection(host+":80")
        h.request('POST', subUrl, data, headers)
        r = h.getresponse()

        headersReturned = r.getheaders()
        cfduid = ""
        for returnedHeader,rValue in headersReturned:
            if returnedHeader == 'set-cookie':
                #print "header1: "+returnedHeader+", value1: "+rValue
                if rValue.find("__cfduid=")>-1:
                    cfduid = rValue[rValue.find("__cfduid="):]
                    if cfduid.find(";")>-1:
                        cfduid = cfduid[0:cfduid.find(";")]
        if cfduid!= '':
            Vigoal.cookie = cfduid
        html = r.read()
        return html