# -*- coding: utf-8 -*-
from core.decoder import Decoder
from core import logger
from core.downloader import Downloader

class Tvshowme(Downloader):

    MAIN_URL = "http://www.tvshow.me/"

    @staticmethod
    def getChannels(page):
        x = []
        logger.debug("using tvshowme...")
        if str(page) == '0':
            page=Tvshowme.MAIN_URL
            html = Tvshowme.getContentFromUrl(page,"",Tvshowme.cookie,"")
            table = Decoder.extract('<span class="yawp_wim_title">Latest 150 Posts</span> <ul>','</ul>',html)
            x = Tvshowme.extractElements(table)
        else:
            html = Tvshowme.getContentFromUrl(page, "", Tvshowme.cookie, Tvshowme.MAIN_URL)
            logger.debug(html)
            table = Decoder.extract('<div id="content"', '</article>', html)
            x = Tvshowme.extractLinks(table)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        i=0
        for value in table.split('<li>'):
            if i>0:
                element = {}
                title = Decoder.extract('/">','</a>',value)
                link = Decoder.extract('<a href="','"',value)
                element["title"] = title
                element["link"] = link
                logger.debug("append: "+title+", link: "+element["link"])
                x.append(element)
            i+=1
        return x

    @staticmethod
    def extractLinks(html):
        x = []
        i=0
        for value in html.split('<a href='):
            if i>1:
                element = {}
                title = Decoder.extract('>','</a>', value)
                link = Decoder.extract('"','"', value)
                element["title"] = title
                element["link"] = link
                element["finalLink"] = True
                if "<img" not in title and "tvshow.me" not in link:
                    logger.debug("append: " + title + ", link: " + element["link"])
                    x.append(element)
            i+=1
        return x