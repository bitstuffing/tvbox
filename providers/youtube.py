# -*- coding: utf-8 -*-

from core import logger
from core.decoder import Decoder
from core.downloader import Downloader

try:
    import json
except:
    import simplejson as json

class Youtube(Downloader):

    MAIN_URL = "https://www.youtube.com"

    @staticmethod
    def getChannels(page='0'):
        x = []
        if str(page) == '0':
            page=Youtube.MAIN_URL+"/"
            html = Youtube.getContentFromUrl(page,"",Youtube.cookie,"")
            logger.debug("html: "+html)
            x = Youtube.extractMainChannels(html)
        elif page.find('/channel/')>-1:
            html = Youtube.getContentFromUrl(page,"",Youtube.cookie,Youtube.MAIN_URL)
            x = Youtube.extractAllVideos(html)
        elif "/trending" in page:
            x = Youtube.extractAllVideosFromHtml(page)
        else:
            html = Youtube.getContentFromUrl(page,"",Youtube.cookie,Youtube.MAIN_URL)
            x = Youtube.extractTargetVideo(html)
        return x

    @staticmethod
    def extractTargetVideo(html):
        logger.debug(html)


    @staticmethod
    def extractAllVideosFromHtml(page):
        x = []
        html = Youtube.getContentFromUrl(page,"",Youtube.cookie,Youtube.MAIN_URL)
        tableHtml = Decoder.extract('class="item-section">','</ol>',html)
        i=0
        for rowHtml in tableHtml.split('<div class="yt-lockup-dismissable yt-uix-tile">'):
            if i>0:
                element = {}
                link = Decoder.extract(' href="', '"', rowHtml)
                title = Decoder.rExtract('title="','" data-sessionlink', rowHtml)
                logger.debug("link: "+link+", title is: "+title)
                if 'youtube.com' not in link:
                    link = Youtube.MAIN_URL+link
                image = Decoder.extractWithRegex('https://i.ytimg.com/','"',rowHtml).replace('"','')
                element["title"] = title
                element["page"] = link
                element["finalLink"] = True
                element["thumbnail"] = image
                x.append(element)
            i+=1
        return x

    @staticmethod
    def extractAllVideos(html):
        x = []
        jsonScript = Decoder.extract('<script type="application/ld+json">','</script>',html).strip()
        #logger.debug("json: "+jsonScript)
        jsonList = json.loads(jsonScript)
        for element in jsonList['itemListElement']:
            #logger.debug("element: "+str(element))
            if element.has_key('item'):
                for element2 in element["item"]["itemListElement"]:
                    #logger.debug("element2: "+str(element2))
                    target = {}
                    target["page"] = str(element2["url"])
                    code = target["page"][target["page"].rfind("=")+1:]
                    target["thumbnail"] = "https://i.ytimg.com/vi/"+code+"/mqdefault.jpg"
                    target["title"] = Decoder.extract('href="/watch?v='+code+'">',"</",html)
                    logger.debug("appended: "+target["title"]+", url: "+target["page"])
                    target["finalLink"] = True
                    x.append(target)
        return x

    @staticmethod
    def extractMainChannels(html):
        x = []
        i = 0
        for value in html.split('guide-item yt-uix-sessionlink yt-valign spf-link'):
            if i>0 and value.find("href=\"")>-1 and value.find('title="')>-1:
                element = {}
                title = Decoder.extract('title="','"',value)
                link = Youtube.MAIN_URL+Decoder.extract('href="','"',value)
                element["title"] = title
                element["page"] = link
                if value.find('<img src="')>-1:
                    element["thumbnail"] = Decoder.extract('<img src="','"',value)
                    logger.debug("thumbnail: "+element["thumbnail"])
                logger.debug("append: "+title+", link: "+element["page"])
                x.append(element)
            i+=1
        return x