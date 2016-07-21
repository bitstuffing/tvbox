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
        else:
            html = Youtube.getContentFromUrl(page,"",Youtube.cookie,Youtube.MAIN_URL)
            x = Youtube.extractTargetVideo(html)
        return x

    @staticmethod
    def extractTargetVideo(html):
        logger.debug(html)

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
                    #http://www.youtube.com/watch?v=kkx-7fsiWgg
                    #https://i.ytimg.com/vi/kkx-7fsiWgg/mqdefault.jpg
                    #<a href="/watch?v=kkx-7fsiWgg" data-sessionlink="ei=rEMZV9-tHoTPcPzgvdgG&amp;feature=c4-overview&amp;ved=CKoBEL8bIhMI37P7htSgzAIVhCccCh18cA9rKJsc" aria-describedby="description-id-3662" title="Hasta el Amanecer - Nicky Jam | Video Oficial" dir="ltr" class="yt-uix-sessionlink yt-uix-tile-link  spf-link  yt-ui-ellipsis yt-ui-ellipsis-2">Hasta el Amanecer - Nicky Jam | Video Oficial</a>
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