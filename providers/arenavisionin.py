# -*- coding: utf-8 -*-
from core.xbmcutils import XBMCUtils
import os
from core.decoder import Decoder
from core import jsunpack
from core import logger
from core.downloader import Downloader

class Arenavisionin(Downloader):

    MAIN_URL = "http://www.arenavision.in/guide"
    MAIN_URL_RU = "http://www.arenavision.ru/guide"

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == '0':
            try:
                page=Arenavisionin.MAIN_URL
                html = Arenavisionin.getContentFromUrl(page,"",'beget=begetok; has_js=1',Arenavisionin.MAIN_URL)
            except:
                page = Arenavisionin.MAIN_URL_RU
                html = Arenavisionin.getContentFromUrl(page, "", 'beget=begetok; has_js=1', Arenavisionin.MAIN_URL_RU)
                pass
            html = Decoder.extract('<table align="center" cellspacing="1" class="auto-style1" style="width: 100%; float: left"><tr><th class="auto-style4" style="width: 190px; height: 39px"><strong>DAY</strong></th>',"</tr></table></div></div></div>",html)
            x = Arenavisionin.extractElements(html)
        else:
            if page.find("-")>-1:
                #put a context menu and the user should decice, if not use the first one (default action)
                dialog = XBMCUtils.getDialog()
                cmenu = []
                for contextItem in page.split("-"):
                    #if len(contextItem)>0:
                    cmenu.append("av"+contextItem)
                result = dialog.select(XBMCUtils.getString(11016), cmenu) #choose
                logger.debug("result was: "+str(result))
                if result == None or result==-1:
                    target = page[:page.find("-")]
                    page = target
                else:
                    logger.debug("has choosed "+str(result)+": "+cmenu[result])
                    page = (cmenu[result])
                link = "http://www.arenavision.in/" + page
            else:
                if "av" not in page:
                    page = "av"+page
                link = "http://www.arenavision.in/"+page
            try:
                html = Arenavisionin.getContentFromUrl(link,"",'beget=begetok; has_js=1',Arenavisionin.MAIN_URL)
            except:
                link = "http://www.arenavision.ru/" + page
                html = Arenavisionin.getContentFromUrl(link, "", 'beget=begetok; has_js=1', Arenavisionin.MAIN_URL_RU)
                pass
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
        for value in table.split('</tr>'):
            if i>0:
                element = {}
                title = Arenavisionin.extractTextFromHTMLValue(value)
                link = Decoder.rExtract('">',"</td>",value)
                if "<" in link:
                    link = link[:link.find("<")]
                if "[" in link:
                    link = link[:link.find("[")]
                if " " in link:
                    link = link[:link.find(' ')]
                element["title"] = title.strip()
                element["link"] = link.strip()
                logger.debug("append: "+title+", link: "+link)
                if len(link)>0 and len(title)>0 and title.find(":")==2:
                    x.append(element)
            i+=1
        return x

    @staticmethod
    def extractTextFromHTMLValue(value):
        #should be <td> so split with that
        text = ""
        for htmlValued in value.split('/td>'):
            if len(text)>0:
                text+= " - "
            target = Decoder.extract(">","<",htmlValued).strip().strip(" ")
            if len(target)>0:
                logger.debug("appending target: "+target)
                text += target
        return text