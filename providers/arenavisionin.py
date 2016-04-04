# -*- coding: utf-8 -*-

import httplib
import urllib
import os
import binascii
from core.decoder import Decoder
from core import jsunpack
from core import logger
from core.downloader import Downloader

class Arenavisionin(Downloader):

    MAIN_URL = "http://www.arenavision.in/agenda"

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == '0':
            page=Arenavisionin.MAIN_URL
            html = Arenavisionin.getContentFromUrl(page,"",Arenavisionin.cookie,"")
            html = Decoder.extract('**CET Time -','<p>**All schedule',html)
            html = Decoder.extract("<p>","</p>",html)
            x = Arenavisionin.extractElements(html)
        else:
            if page.find("/")>-1:
                link = "http://www.arenavision.in/"+page[:page.find("/")]
            else:
                link = "http://www.arenavision.in/"+page
            html = Arenavisionin.getContentFromUrl(link,"",Arenavisionin.cookie,Arenavisionin.MAIN_URL)
            if html.find("acestream://")>-1:
                link2 = Decoder.extractWithRegex("acestream://",'"',html).replace('"',"")
            else:
                link2 = Decoder.extractWithRegex("sop://",'"',html).replace('"',"")
            element = {}
            element["title"] = page
            element["link"] = link2
            x.append(element)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        i = 0
        for value in table.split('<br/>'):
            element = {}
            title = value[0:value.find(")/")+1]
            link = value[value.find(")/")+2:]
            element["title"] = title
            element["link"] = link
            logger.debug("append: "+title+", link: "+element["link"])
            x.append(element)
            i+=1
        return x