import httplib
import urllib
import os
import binascii
from core.decoder import Decoder
from core import jsunpack
from core import logger
from providers.cricfreetv import Cricfreetv

class Sports4u():

    cookie = ""
    MAIN_URL = "http://live.sports4u.tv/"

    @staticmethod
    def getChannels(page):
        x = []
        start = False
        if str(page) == '0':
            start = True
            page=Sports4u.MAIN_URL
        html = Sports4u.getContentFromUrl(page,"",Sports4u.cookie,"")
        #print html
        if start and html.find('<div class="col-md-2 col-sm-12 col-xs-12 live-channels-list">')>-1: #it's a list, needs decode
            table = Decoder.extract('<div class="col-md-2 col-sm-12 col-xs-12 live-channels-list">','</ul>',html)
            x = Sports4u.extractElements(table)
            logger.info("channel list logic done!")
        else:
            iframeUrl = Decoder.extract('<iframe frameborder="0" marginheight="0" marginwidth="0" height="490" ','"></iframe>',html)
            iframeUrl = Decoder.extract('src="','"',iframeUrl)
            logger.info("iframeUrl is: "+iframeUrl)
            html2 = Sports4u.getContentFromUrl(iframeUrl,"",Sports4u.cookie,page)
            #print html2
            file = Cricfreetv.seekIframeScript(html2,page,iframeUrl)
            logger.info("Finished file logic, obtained file: "+file)
            element = {}
            element["link"] = file
            element["title"] = "Watch streaming"
            x.append(element)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        for fieldHtml in table.split('<li>'):
            if fieldHtml.find("<a href=")>-1:
                element = {}
                element["link"] = Decoder.extract('<a href="','"',fieldHtml)
                element["title"] = Decoder.extract('alt="','">',fieldHtml)
                element["thumbnail"] = Decoder.extract('src="','" ',fieldHtml)
                logger.info("found title: "+element["title"]+", link: "+element["link"]+", thumbnail: "+element["thumbnail"])
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
            Sports4u.cookie = cfduid
        logger.info("cookie was updated to: "+Sports4u.cookie)
        html = r.read()
        if location != '':
            logger.info("launching redirection to: "+location)
            html = Sports4u.getContentFromUrl(location,data,Sports4u.cookie,url)
        return html