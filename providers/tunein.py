import urllib

from core.downloader import Downloader
from core.decoder import Decoder
from core.xbmcutils import XBMCUtils
from core import logger

class TuneIn(Downloader):

    SEARCH_PAGE = "http://tunein.com/search/?query="
    MAIN_URL = "http://tunein.com"

    @staticmethod
    def getChannels(page):
        x = []
        if page == '0':
            keyboard = XBMCUtils.getKeyboard()
            keyboard.doModal()
            text = ""
            if (keyboard.isConfirmed()):
                text = keyboard.getText()
                if len(text)>0:
                    page = TuneIn.SEARCH_PAGE+urllib.quote_plus(text)
                    resultHtml = TuneIn.getContentFromUrl(page,ajax=True,referer=TuneIn.MAIN_URL)
                    logger.debug("resultHtml is: "+resultHtml)
                    results = Decoder.extract('"GuideItems": [','"pageTitle": "Search results for ',resultHtml)
                    i=0
                    for result in results.split('"GuideId": "'):
                        if i>0:
                            element = {}
                            img = Decoder.extract('"Image": "','"',result)
                            link = TuneIn.MAIN_URL+Decoder.extract('"Url": "', '"', result)
                            title = Decoder.extract('"Title": "', '"', result)
                            logger.debug("appending result: "+title+", url: "+link)
                            element["title"] = title
                            element["link"] = link
                            element["thumbnail"] = img
                            element["finalLink"] = True
                            x.append(element)
                        i+=1
        else:
            logger.debug("extracting stream for: "+page)
            content = TuneIn.getContentFromUrl(url=page,referer=TuneIn.MAIN_URL)
            logger.debug("list content is: " + content)
            url = "http://"+Decoder.extract('"StreamUrl":"//','"',content)
            title = Decoder.extract('"Title": "','"',content)
            img = Decoder.extract('"Image": "','",',content)
            logger.debug("url is: " + url)
            html = TuneIn.getContentFromUrl(url=url,referer=page)
            logger.debug("decoded html is: "+html)
            listUrl = Decoder.extract('"Url": "','"',html)
            element = {}
            element["link"] = listUrl
            element["title"] = title
            element["thumbnail"] = img
            x.append(element)
        return x

