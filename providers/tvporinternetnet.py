# -*- coding: utf-8 -*-
import urllib
from tvboxcore.decoder import Decoder
from tvboxcore import logger
from tvboxcore.downloader import Downloader

class Tvporinternetnet(Downloader):

    MAIN_URL = "http://tvpor-internet.com/channels"

    @staticmethod
    def getChannels(page):
        if str(page) == '0':
            page=Tvporinternetnet.MAIN_URL

        page = urllib.unquote_plus(page)
        html = Tvporinternetnet.getContentFromUrl(page,"",Tvporinternetnet.cookie,"")
        x = []
        if page == Tvporinternetnet.MAIN_URL:
            table = Decoder.extract('<div id="canalesdown" class="canales">',"<br>",html)
            for fieldHtml in table.split('<li'):
                element = {}
                element["link"] = Decoder.extract('<a href="','"',fieldHtml)
                element["title"] = Decoder.extract('<div style="color: #ffffff;">','<',fieldHtml)
                element["thumbnail"] = Decoder.extract('<img src="','"',fieldHtml)
                element["permaLink"] = True
                logger.debug("found title: "+element["title"]+", link: "+element["link"]+", thumb: "+element["thumbnail"])
                if "http" in element["link"]:
                    x.append(element)
        else:
            x.append(Tvporinternetnet.extractChannel(html,page))
        return x

    @staticmethod
    def extractChannel(html,page="http://tvpor-internet.com"):
        element = {}
        if "<script type='text/javascript'>" in html: #old part
            script = Decoder.extract("<script type='text/javascript'>","</",html)
            cosa = Decoder.extract("cosa = '","'",script)
            id = Decoder.extract("id='", "'", script)
            scriptUrl = "http://tvpor-internet.com/player/"+cosa+"/"+id
            html2 = Tvporinternetnet.getContentFromUrl(scriptUrl)
            lastUrl = Decoder.extract('<source src="','"',html2)
            logger.debug("decoded link is: "+lastUrl)
            element["title"] = page
            element["link"] = lastUrl
        return element
