# -*- coding: utf-8 -*-

import httplib
import urllib
import os
import binascii
from core.decoder import Decoder
from core import jsunpack
from core import logger
from core.downloader import Downloader

class Skylinewebcamscom(Downloader):

    MAIN_URL = "http://www.skylinewebcams.com/"

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == '0':
            page=Skylinewebcamscom.MAIN_URL
        html = Skylinewebcamscom.getContentFromUrl(page,"",Skylinewebcamscom.cookie,"")
        if page.find(".html")==-1:
            logger.info("browsing main menu...")
            menu = Decoder.extract('<ul class="nav" id="main-menu">',"</li></ul></li></ul>",html)
            x = Skylinewebcamscom.extractElements(menu)
        else:
            logger.info("browsing page...")
            if html.find('<ul class="hidden-xs nav nav-tabs')>-1:
                logger.info("browsing submenu")
                menu = Decoder.extract('<ul class="hidden-xs nav nav-tabs','</li></ul>',html) #first tries to extract submenu
                x = Skylinewebcamscom.extractElements(menu)
                if len(x)==0: #no submenu, so final channels have to been extracted
                    logger.info("browsing webcams")
                    content = Decoder.extract('<ul class="row list-unstyled block webcams">','</li></ul>',html)
                    x = Skylinewebcamscom.extractElements(content)
            else:
                logger.info("building url for webcam...")
                if html.find(",url:'")==-1: #needs subchannels
                    logger.info("browsing webcams")
                    content = Decoder.extract('<ul class="row list-unstyled block webcams">','</li></ul>',html)
                    x = Skylinewebcamscom.extractElements(content)
                else: #final channel
                    url = Decoder.extract(",url:'","'",html)
                    logger.info("building final link: "+url)
                    element = {}
                    element["title"] = "Webcam"
                    element["link"] = url
                    element["permaLink"] = True
                    x.append(element)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        i = 0
        for value in table.split('<a '):
            logger.info("loop: "+str(i))
            if i>0:
                element = {}
                if value.find('<img ')==-1:
                    title = Decoder.rExtract(">",'</a></li>',value)
                    link = Decoder.extract("href=\"/",'"',value)
                    element["title"] = title
                    element["link"] = Skylinewebcamscom.MAIN_URL+link
                    if len(title)>0 and link.find("#")==-1 and len(element["link"])>len(Skylinewebcamscom.MAIN_URL) and (title.find("<")==-1 and title.find(">")==-1):
                        logger.info("append: "+title+", link: "+element["link"])
                        x.append(element)
                    else:
                        logger.info("discarted: "+title+", link: "+element["link"])
                else:
                    img = "http://"+Decoder.extract("data-original=\"//",'" ',value)
                    title = Decoder.extract("class=\"title\">",'</span>',value)
                    link = Decoder.extract("href=\"/",'"',value)
                    element["title"] = title
                    element["link"] = Skylinewebcamscom.MAIN_URL+link
                    element["thumbnail"] = img
                    element["permaLink"] = True
                    if link.find(".html")>-1 and (title.find("<")==-1 and title.find(">")==-1):
                        logger.info("append: "+title+", link: "+element["link"]+", img: "+element["thumbnail"])
                        x.append(element)
                    else:
                        logger.info("discarted: "+title+", link: "+element["link"]+", img: "+element["thumbnail"])
            i+=1
        return x