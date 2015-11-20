import httplib
import urllib
from core.decoder import Decoder
from core import logger

class Vigoal():

    cookie = ""
    MAIN_URL = "http://www.vipgoal.net/"

    @staticmethod
    def getChannels(page):
        start = False
        #logger.info("Current page is: "+page)
        if str(page) == '0' or str(page)=='1':
            if str(page)=='0':
                start = True
            page=Vigoal.MAIN_URL
        html = Vigoal.getContentFromUrl(page,"",Vigoal.cookie,"")
        x = []
        if page.find(".html")==-1:
            if start:
                element = {}
                element["link"] = '1'
                element["title"] = 'Display by event'
                x.append(element)
                table = Decoder.extract("<center><table><tbody><tr>","</center>",html)
                for fieldHtml in table.split('<a href="'):
                    element = {}
                    element["link"] = fieldHtml[0:fieldHtml.find('"')]
                    element["title"] = fieldHtml[fieldHtml.find('title="')+len('title="'):]
                    element["title"] = element["title"][0:element["title"].find('"')]
                    element["thumbnail"] = fieldHtml[fieldHtml.find('<img src="')+len('<img src="'):]
                    element["thumbnail"] = element["thumbnail"][0:element["thumbnail"].find('"')]
                    logger.info("found title: "+element["title"]+", link: "+element["link"]+", thumb: "+element["thumbnail"])
                    if element["link"].find("http")==0:
                        x.append(element)
            else: #display program content
                table = Decoder.extract("<h2>Events Today:</h2>","</ul>",html) #instead could be used <div class="ppal"> but... fate I suppose
                i = 0
                for fieldHtml in table.split('<li class="">'):
                    if i>0:
                        element = {}
                        element["link"] = Decoder.extract('<a href="','">',fieldHtml)
                        element["title"] = Decoder.extract(' - ','</div>',fieldHtml)
                        if fieldHtml.find('"><h2>')>-1:
                            titleLine = Decoder.extract('"><h2>',"</h2>",fieldHtml)
                        else:
                            titleLine = Decoder.rExtract('html">',"</a></div>",fieldHtml)
                        element["title"] = titleLine+" - "+(element["title"].replace("</b>","").replace(" - ",""))
                        element["thumbnail"] = fieldHtml[fieldHtml.find('<img src="')+len('<img src="'):]
                        element["thumbnail"] = Vigoal.MAIN_URL+element["thumbnail"][0:element["thumbnail"].find('"')]
                        logger.info("found title: "+element["title"]+", link: "+element["link"]+", thumb: "+element["thumbnail"])
                        element["link"] = Vigoal.MAIN_URL+element["link"]
                        x.append(element)
                    i+=1
        else:
            x.append(Vigoal.extractChannel(html))
        return x

    @staticmethod
    def extractChannel(html):
        element = {}
        if html.find('<script type="text/javascript" src="http://www.playerapp1.pw/channel.php?file=')>-1:
            scriptUrl = Decoder.extractWithRegex('http://www.playerapp1.pw/channel.php?file=','"',html)
            html2 = Vigoal.getContentFromUrl(scriptUrl)
            lastUrl = Decoder.extractWithRegex('http://','" ',html2)
            lastUrl = lastUrl.replace('"',"")
            logger.info("last url: "+lastUrl+", cookie="+Vigoal.cookie)
            html3 = Vigoal.getContentFromUrl(lastUrl,"",Vigoal.cookie,lastUrl)
            playerUrl = Decoder.decodeBussinessApp(html3,lastUrl)
            logger.info("player url is: "+playerUrl)
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
        location = ""
        for returnedHeader,rValue in headersReturned:
            if returnedHeader == 'set-cookie':
                #print "header1: "+returnedHeader+", value1: "+rValue
                if rValue.find("__cfduid=")>-1:
                    cfduid = rValue[rValue.find("__cfduid="):]
                    if cfduid.find(";")>-1:
                        cfduid = cfduid[0:cfduid.find(";")]
            elif returnedHeader == 'location':
                logger.info("Location detected: using location: "+rValue)
                location = rValue
            else:
                logger.info("rejected cookie: "+returnedHeader+", "+rValue)
        if cfduid!= '':
            Vigoal.cookie = cfduid
        logger.info("cookie was updated to: "+Vigoal.cookie)
        html = r.read()
        if location != '':
            logger.info("launching redirection to: "+location)
            html = Vigoal.getContentFromUrl(location,data,Vigoal.cookie,url)
        return html