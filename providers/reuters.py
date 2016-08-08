import time
import re
try:
    import json
except:
    import simplejson as json

from core.downloader import Downloader
from core.decoder import Decoder
from core import logger

class Reuters(Downloader):

    MAIN_URL = "http://www.reuters.com"
    LAST_NEWS_RSS = "http://www.reuters.com/assets/jsonWireNews?startTime="

    @staticmethod
    def getChannels(page):
        x = []
        if page == '0':
            url = Reuters.LAST_NEWS_RSS + str(time.time() * 1000)
            logger.debug("news rss url is: "+url)
            bruteResult = Reuters.getContentFromUrl(url=url,launchLocation=False,ajax=True)
            logger.debug("brute ajax response: "+bruteResult)
            results = json.loads(bruteResult)
            i=0
            for result in results["headlines"]:
                if i>0:
                    element = {}
                    img = result["mainPicUrl"]
                    link = Reuters.MAIN_URL+result["url"]
                    title = result["formattedDate"]+" - "+result["headline"]
                    logger.debug("appending result: "+title+", url: "+link+", img: "+img)
                    element["title"] = title
                    element["link"] = link
                    element["thumbnail"] = img
                    x.append(element)
                i+=1
        else:
            html = Reuters.getContentFromUrl(url=page)
            body = Decoder.extract('<span id="articleText">','<div class="linebreak"></div>',html)
            body = Decoder.removeHTML(body)
            try:
                lowerCaseIndex = int(re.search("[a-z]", body).start())
                body = body[:lowerCaseIndex-1]+"\n"+body[lowerCaseIndex-1:]
            except:
                logger.error("No break for city was done. Something goes wrong")
                pass
            element = {}
            element["link"] = page
            element["title"] = body
            element["thumbnail"] = ''
            x.append(element)
        return x

