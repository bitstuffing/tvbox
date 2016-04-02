import httplib
import urllib
import os
import binascii
from core.decoder import Decoder
from core import jsunpack
from core import logger
from core.downloader import Downloader

class Live9net(Downloader):

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
            logger.debug("live9 channels logic done!")
        else:
            iframeUrl = Decoder.extract('src="','"></iframe>',html)
            html2 = Live9net.getContentFromUrl(iframeUrl,"",Live9net.cookie,page)
            #print html2
            if html2.find('src="http://sawlive.tv/')>-1 or html2.find('src="http://www3.sawlive')>-1:
                if html2.find('src="http://sawlive.tv/')>-1:
                    scriptSrc = Decoder.extractWithRegex('http://sawlive','"></script>',html2).replace('"></script>',"")
                else:
                    scriptSrc = Decoder.extractWithRegex('http://www3.sawlive','"></script>',html2).replace('"></script>',"")
                finalRtmpUrl = Decoder.extractSawlive(scriptSrc,iframeUrl)
                element = {}
                element["link"] = finalRtmpUrl
                element["title"] = "Watch channel"
                element["permalink"] = True
                logger.debug("finished append element!")
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
                logger.debug("found title: "+element["title"]+", link: "+element["link"])
                if len(element["title"])>0:
                    x.append(element)

        return x