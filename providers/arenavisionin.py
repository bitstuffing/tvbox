# -*- coding: utf-8 -*-

import xbmcaddon, xbmcgui
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
                #put a context menu and the user should decice, if not use the first one (default action)
                dialog = xbmcgui.Dialog()
                cmenu = []
                for contextItem in page.split("/"):
                    if len(contextItem)>1:
                        cmenu.append(contextItem)
                addon = xbmcaddon.Addon(id='org.harddevelop.kodi.tv')
                result = dialog.select(addon.getLocalizedString(11016), cmenu) #choose
                logger.debug("result was: "+str(result))
                if result == None or result==-1:
                    link = "http://www.arenavision.in/"+page[:page.find("/")]
                else:
                    logger.debug("has choosed "+str(result)+": "+cmenu[result])
                    link = "http://www.arenavision.in/"+(cmenu[result])
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