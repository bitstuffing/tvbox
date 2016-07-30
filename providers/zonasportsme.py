# -*- coding: utf-8 -*-
import urllib2
import urllib
import os,re
import base64
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
            url = ""
            #decoder part
            if 'http://www.ustream.tv/' in html:
                uStreamUrl = Decoder.extractWithRegex('http://www.ustream.','"',html)
                url = Decoder.getUstreamLink(uStreamUrl,page)
            elif 'castamp.com/embed.js' in html:
                channel = Decoder.extract('channel="','"',html)
                url = Decoder.getCastcampLink(channel,page)
            elif 'adca.st/broadcast/player.js' in html:
                id2 = Decoder.extract("<script type='text/javascript'>id='", "';", html)
                logger.debug("using id = " + id2)
                url4 = "http://greenhome.online/stream.php?id=" + id2 + "&width=700&height=450&stretching=uniform"
                html4 = Zonasportsme.getContentFromUrl(url4, "", Zonasportsme.cookie, page)
                logger.debug("html4: " + html4)
                curl = Decoder.extract('curl = "', '"', html4)
                token = Zonasportsme.getContentFromUrl('http://greenhome.online/getToken.php', "",Zonasportsme.cookie, url4, True)
                logger.debug("token: " + token)
                token = Decoder.extract('":"', '"', token)
                file = base64.decodestring(curl) + token + "|" + Downloader.getHeaders('http://cdn.allofme.site/jw/jwplayer.flash.swf')
                logger.debug("final url is: " + file)
                url = file

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

    @staticmethod
    def getContent(url, referer="",proxy=None, post=None):
        timeout='14'
        result = ""
        headers = {}
        try:
            handlers = []
            handlers += [urllib2.ProxyHandler({'http':'%s'%(proxy)}),urllib2.HTTPHandler]
            opener = urllib2.build_opener(*handlers)
            opener = urllib2.install_opener(opener)
            headers['User-Agent'] = Downloader.USER_AGENT
            if referer != "":
                headers['referer'] = referer
            headers['Accept-Language'] = 'en-US'
            request = urllib2.Request(url, data=post, headers=headers)
            try:
                response = urllib2.urlopen(request, timeout=int(timeout))
            except urllib2.HTTPError as response:
                pass
            result = response.read(1024 * 1024) #without buffer sometimes it does not work :'(
            response.close()
        except:
            logger.error("something wrong happened with this url: "+url)
        return result