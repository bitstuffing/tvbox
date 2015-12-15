# -*- coding: utf-8 -*-

import httplib
import urllib
import os
import base64
import binascii
from core.decoder import Decoder
from core import jsunpack
from core import logger
from core.downloader import Downloader
from providers.cricfreetv import Cricfreetv

class Zonasportsme(Downloader):

    MAIN_URL = "http://zonasports.me/"

    @staticmethod
    def getChannels(page):
        x = []
        logger.info("page is: "+page)
        if str(page) == '0':
            page=Zonasportsme.MAIN_URL
        else:
            logger.info("decoding page: "+page)
            page = base64.b64decode(page)
            logger.info("decoded page: "+page)
        logger.info("launching web petition to page: "+page)
        html = Zonasportsme.getContentFromUrl(page,"",Zonasportsme.cookie,Zonasportsme.MAIN_URL)
        if page==Zonasportsme.MAIN_URL:
            logger.info("browsing main menu...")
            menu = Decoder.extract('<ul class="nav" id="main-menu">',"</li></ul></li></ul>",html)
            x = Zonasportsme.extractElements(menu)
        else:
            #print html
            url = ""
            if html.find('var t="')>-1:
                content = Decoder.extract('var t="','";',html)
                content = bytearray.fromhex(content).decode() #now decode hexadecima string to plain text
                url = Decoder.extract("'file': '","'",content)
                logger.info("found a link: "+url)
                if url.find(".m3u8")==-1:
                    logger.info("unescape logic...")
                    extracted = Decoder.extract('document.write(unescape("','"));',html).decode('unicode-escape', 'ignore')
                    logger.info("extracted unicode was (3 cases to be detected): "+extracted)
                    if extracted.find('file: "')>-1:
                        url = Decoder.extract('file: "','",',extracted)
                    elif extracted.find("'file': '")>-1:
                        url = Decoder.extract("'file': '","',",extracted)
                    elif extracted.find(' src="'+Zonasportsme.MAIN_URL)>-1:
                        page = Decoder.extractWithRegex(Zonasportsme.MAIN_URL,'"',extracted)
                        logger.info("detected embed other channel, relaunching with page: \""+page)
                        return Zonasportsme.getChannels(base64.b64encode(page[:len(page)-1]))
            elif html.find("http://direct-stream.org/embedStream.js")>-1:
                iframeUrl = ""
                scriptUrl = "http://direct-stream.org/embedStream.js"
                scriptContent = Zonasportsme.getContentFromUrl(scriptUrl,"","",page)
                iframeUrl = Decoder.extract('src="','"',scriptContent)
                if iframeUrl.find("?id=")>-1:
                    if html.find('<script type="text/javascript"> fid="')>-1:
                        id = Decoder.extract('<script type="text/javascript"> fid="','";',html)
                        iframeUrl = iframeUrl[0:iframeUrl.find('?id=')+len('?id=')]+id+Cricfreetv.getWidthAndHeightParams(html)
                    else:
                        logger.info("unescape logic...")
                        extracted = Decoder.extract('document.write(unescape("','"));',html).decode('unicode-escape', 'ignore')
                        logger.info("extracted unicode was (no cases): "+extracted)
                        #search for .m3u8 file
                        url = Decoder.extract('file: "','",',extracted)
                else:
                    iframeUrl = Decoder.extract("<iframe src='","' ",scriptContent)
                if url == '':
                    html2 = Zonasportsme.getContentFromUrl(iframeUrl,"","",page)
                    url2 = Decoder.extract('top.location="','"',html2)#+page
                    logger.info("using location url: "+url2)
                    #html3 = Zonasportsme.getContentFromUrl(url2,"",Zonasportsme.cookie,iframeUrl)
                    html3 = Zonasportsme.getContentFromUrl(url2,"",Zonasportsme.cookie,url2)
                    #print html3
                    swfUrl = "http://direct-stream.biz/jwplayer/jwplayer.flash.swf"
                    tcUrl = Decoder.extract('var file1 = "','";',html3)
                    playPath = tcUrl[tcUrl.rfind('/'):]
                    url = tcUrl+" swfUrl="+swfUrl+" playPath="+playPath+" live=1 pageUrl="+url2
                    logger.info("built rtmp url: "+url)
            else:
                #http://www.byetv.org/channel.php?file=2099&width=700&height=400&autostart=true
                logger.info("unescape logic...")
                extracted = Decoder.extract('document.write(unescape("','"));',html).decode('unicode-escape', 'ignore')
                logger.info("extracted unicode was (no cases 2): "+extracted)
                #search for .m3u8 file
                if extracted.find('file: "')>-1:
                    url = Decoder.extract('file: "','",',extracted)
                elif extracted.find(' src="'+Zonasportsme.MAIN_URL)>-1:
                    page = Decoder.extractWithRegex(Zonasportsme.MAIN_URL,'"',extracted)
                    logger.info("detected embed other channel, relaunching with page: \""+page)
                    return Zonasportsme.getChannels(base64.b64encode(page[:len(page)-1])) ##TODO, remake this part because there are some links that could not being working
            element = {}
            element["title"] = "Stream"
            element["link"] = url
            element["permaLink"] = True
            x.append(element)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        i = 0
        for value in table.split('<li>'):
            logger.info("loop: "+str(i))
            if i>0:
                element = {}
                title = Decoder.extract(">",'</a></li>',value)
                link = Decoder.extract("href=\"",'"',value)
                element["title"] = title
                element["link"] = base64.b64encode(str(Zonasportsme.MAIN_URL+link))
                logger.info("append: "+title+", link: "+element["link"])
                x.append(element)
            i+=1
        return x