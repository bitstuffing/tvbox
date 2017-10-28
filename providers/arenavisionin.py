# -*- coding: utf-8 -*-
from core.xbmcutils import XBMCUtils
import os
from core.decoder import Decoder
from core import jsunpack
from core import logger
from core.downloader import Downloader

class Arenavisionin(Downloader):

    MAIN_URL = "http://www.arenavision.us/iguide"
    MAIN_URL_RU = "http://www.arenavision.ru/iguide"

    COOKIE = "has_js=1; POPARENArhpmax=3|Sat%2C%2014%20Oct%202017%2018%3A26%3A06%20GMT; ads_smrt_popunder=2%7CSun%2C%2015%20Oct%202017%2017%3A26%3A02%20GMT; POPARENArhpmin=yes"

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
                    cmenu.append(contextItem)
                result = dialog.select(XBMCUtils.getString(11016), cmenu) #choose
                logger.debug("result was: "+str(result))
                if result == None or result==-1:
                    target = page[:page.find("-")]
                    page = target
                else:
                    logger.debug("has choosed "+str(result)+": "+cmenu[result])
                    page = (cmenu[result])
                if len(page)== 1:
                    page = "0"+str(page)
                link = "http://www.arenavision.us/" + page
            else:
                if "av" not in page:
                    page = "av"+page
                link = "http://www.arenavision.us/"+page
            try:
                html = Arenavisionin.getContentFromUrl(link,"",Arenavisionin.COOKIE,Arenavisionin.MAIN_URL)
            except:
                if len(page)== 1:
                    page = "0"+str(page)
                link = "http://www.arenavision.ru/" + page
                html = Arenavisionin.getContentFromUrl(link, "", Arenavisionin.COOKIE, Arenavisionin.MAIN_URL_RU)
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