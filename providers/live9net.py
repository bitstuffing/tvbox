import httplib
import urllib
import os
import binascii
from core.decoder import Decoder
from core import jsunpack
from core import logger

class Live9net():

    cookie = ""
    MAIN_URL = "http://live9.net/"

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == '0':
            page=Live9net.MAIN_URL
        html = Live9net.getContentFromUrl(page,"",Live9net.cookie,"")
        #print html
        if html.find('ESPN</')>-1: #it's a list, needs decode
            table = Decoder.extract('ESPN</','<div>',html)
            x = Live9net.extractElements(table)
            print "done!"
        else:
            iframeUrl = Decoder.extract('src="','"></iframe>',html)
            html2 = Live9net.getContentFromUrl(iframeUrl,"",Live9net.cookie,page)
            #print html2
            if html2.find('src="http://sawlive.tv/')>-1 or html2.find('src="http://www3.sawlive')>-1:
                if html2.find('src="http://sawlive.tv/')>-1:
                    scriptSrc = Decoder.extractWithRegex('http://sawlive','"></script>',html2).replace('"></script>',"")
                else:
                    scriptSrc = Decoder.extractWithRegex('http://www3.sawlive','"></script>',html2).replace('"></script>',"")
                encryptedHtml = Live9net.getContentFromUrl(scriptSrc,"",Live9net.cookie,iframeUrl)
                #print encryptedHtml
                firstIframeUrl = urllib.unquote(Decoder.extract("unescape('","')+'/'+",encryptedHtml))
                secondIframeUrl = urllib.unquote(Decoder.extract("'/'+unescape('","')+'/'+",encryptedHtml))
                thirdIframeUrl = urllib.unquote(Decoder.extract("var chz='","';var",encryptedHtml))
                fourthIframeUrl = Decoder.extract("var za3='","';",encryptedHtml)
                decryptedUrl = "http://"+firstIframeUrl+"/"+secondIframeUrl+"/"+thirdIframeUrl+"/"+fourthIframeUrl
                logger.info("Decrypted url is: "+decryptedUrl)
                html3 = Live9net.getContentFromUrl(decryptedUrl,"",Live9net.cookie,scriptSrc)
                #ok, now extract flash script content
                flashContent = Decoder.extract("var so = new SWFObject('","</script>",html3)
                file = Decoder.extract("'file', '","');",flashContent)
                rtmpUrl = Decoder.extract("'streamer', '","');",flashContent)
                finalRtmpUrl = rtmpUrl+" playpath="+file+" swfUrl=http://static3.sawlive.tv/player.swf live=1 conn=S:OK pageUrl="+decryptedUrl+" timeout=12"
                element = {}
                element["link"] = finalRtmpUrl
                element["title"] = "Watch channel"
                element["permalink"] = True
                x.append(element)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        for fieldHtml in table.split('</a>'):
            if fieldHtml.find("<a href=")>-1:
                element = {}
                element["link"] = Decoder.extract('<a href="','"',fieldHtml)
                title = fieldHtml[fieldHtml.find(":")-2:]
                title = title[0:title.find('<a href="')]
                title = title.replace('<font color="#ffea01"><b>'," - ").replace('</b></font>'," -")
                element["title"] = title
                logger.info("found title: "+element["title"]+", link: "+element["link"])
                if len(element["title"])>0:
                    x.append(element)

        return x

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
            Live9net.cookie = cfduid
        logger.info("cookie was updated to: "+Live9net.cookie)
        html = r.read()
        if location != '':
            logger.info("launching redirection to: "+location)
            html = Live9net.getContentFromUrl(location,data,Live9net.cookie,url)
        return html