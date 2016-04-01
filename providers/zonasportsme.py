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
        logger.debug("page is: "+page)
        if str(page) == '0':
            page=Zonasportsme.MAIN_URL
        else:
            logger.debug("decoding page: "+page)
            page = base64.b64decode(page)
            logger.debug("decoded page: "+page)
        logger.debug("launching web petition to page: "+page)
        html = Zonasportsme.getContentFromUrl(page,"",Zonasportsme.cookie,Zonasportsme.MAIN_URL)
        if page==Zonasportsme.MAIN_URL:
            logger.debug("browsing main menu...")
            menu = Decoder.extract('<ul class="nav" id="main-menu">',"</li></ul></li></ul>",html)
            x = Zonasportsme.extractElements(menu)
        else:
            #print html
            url = ""
            if html.find('var t="')>-1:
                content = Decoder.extract('var t="','";',html)
                #content = bytearray.fromhex(content).decode() #now decode hexadecima string to plain text
                try: #this fix is for an issue related to Android port
                    content = bytearray.fromhex(content).decode()
                except TypeError:  # Work-around for Python 2.6 bug
                    content = bytearray.fromhex(unicode(content)).decode()
                logger.debug("content: "+content)
                url = Decoder.extract("'file': '","'",content)
                logger.debug("found a link: "+url)
                if url.find(".m3u8")==-1:
                    logger.debug("unescape logic...")
                    extracted = Decoder.extract('document.write(unescape("','"));',html).decode('unicode-escape', 'ignore')
                    logger.debug("extracted unicode was (3 cases to be detected): "+extracted)
                    if extracted.find('file: "')>-1:
                        url = Decoder.extract('file: "','",',extracted)
                    elif extracted.find("'file': '")>-1:
                        url = Decoder.extract("'file': '","',",extracted)
                    elif extracted.find(' src="'+Zonasportsme.MAIN_URL)>-1:
                        page = Decoder.extractWithRegex(Zonasportsme.MAIN_URL,'"',extracted)
                        logger.debug("detected embed other channel, relaunching with page: \""+page)
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
                        logger.debug("unescape logic...")
                        extracted = Decoder.extract('document.write(unescape("','"));',html).decode('unicode-escape', 'ignore')
                        logger.debug("extracted unicode was (no cases): "+extracted)
                        #search for .m3u8 file
                        url = Decoder.extract('file: "','",',extracted)
                else:
                    iframeUrl = Decoder.extract("<iframe src='","' ",scriptContent)
                if url == '':
                    html2 = Zonasportsme.getContentFromUrl(iframeUrl,"","",page)
                    url2 = Decoder.extract('top.location="','"',html2)#+page
                    logger.debug("using location url: "+url2)
                    #html3 = Zonasportsme.getContentFromUrl(url2,"",Zonasportsme.cookie,iframeUrl)
                    html3 = Zonasportsme.getContentFromUrl(url2,"",Zonasportsme.cookie,url2)
                    #print html3
                    swfUrl = "http://direct-stream.biz/jwplayer/jwplayer.flash.swf"
                    tcUrl = Decoder.extract('var file1 = "','";',html3)
                    playPath = tcUrl[tcUrl.rfind('/'):]
                    url = tcUrl+" swfUrl="+swfUrl+" playPath="+playPath+" live=1 pageUrl="+url2
                    logger.debug("built rtmp url: "+url)
            elif html.find("http://js.p2pcast.tech/p2pcast/player.js")>-1:
                id = Decoder.extract("<script type='text/javascript'>id='","'",html)
                newReferer = "http://p2pcast.tech/stream.php?id="+id+"&osr=0&p2p=0&stretching=uniform"
                html2 = Zonasportsme.getContentFromUrl(newReferer,"",Zonasportsme.cookie,page)
                html3 = Zonasportsme.getContentFromUrl('http://p2pcast.tech/getTok.php',"",Zonasportsme.cookie,newReferer)
                token = Decoder.extract('{"token":"','"}',html3)
                logger.debug("token: "+token)
                base64Url = Decoder.extract('&p2p=1&stretching=uniform&osr="</script><script>',';',html2)
                logger.debug("provisional: "+base64Url)
                base64Url = Decoder.extract('"','"',base64Url)
                url = base64.decodestring(base64Url)+token+"|Referer=http://cdn.p2pcast.tech/jwplayer.flash.swf"
            else:
                #http://www.byetv.org/channel.php?file=2099&width=700&height=400&autostart=true
                logger.debug("unescape logic...")
                extracted = Decoder.extract('document.write(unescape("','"));',html).decode('unicode-escape', 'ignore')
                logger.debug("extracted unicode was (no cases 2): "+extracted)
                #search for .m3u8 file
                if extracted.find('file: "')>-1:
                    url = Decoder.extract('file: "','",',extracted)
                elif extracted.find('var stream = "')>-1:
                    url = Decoder.extract('var stream = "','";',extracted)
                elif extracted.find(' src="'+Zonasportsme.MAIN_URL)>-1:
                    page = Decoder.extractWithRegex(Zonasportsme.MAIN_URL,'"',extracted)
                    logger.debug("detected embed other channel, relaunching with page: \""+page)
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
            logger.debug("loop: "+str(i))
            if i>0:
                element = {}
                title = Decoder.extract(">",'</a></li>',value)
                link = Decoder.extract("href=\"",'"',value)
                element["title"] = title
                element["link"] = base64.b64encode(str(Zonasportsme.MAIN_URL+link))
                logger.debug("append: "+title+", link: "+element["link"])
                x.append(element)
            i+=1
        return x