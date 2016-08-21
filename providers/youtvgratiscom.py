from core.downloader import Downloader
from core.decoder import Decoder
from core import logger

from providers.cinestrenostv import Cineestrenostv

class Youtvgratis(Downloader):

    MAIN_URL = "http://youtvgratis.com/index.html"

    @staticmethod
    def getChannels(page):
        x = []
        if page == '0':
            html = Youtvgratis.getContentFromUrl(url=Youtvgratis.MAIN_URL)
            i=0
            for line in html.split('<div class="col-xs-12 col-sm-2'):
                if i>0:
                    title = Decoder.extract('</a>','</div>',line)
                    img = Decoder.extract(' src="', '"', line)
                    link = Decoder.extract('<a href="', '"', line)
                    element = {}
                    element["link"] = link
                    element["title"] = title
                    element["thumbnail"] = img
                    logger.debug("appending img: "+img+", title: "+title+", link: "+link)
                    x.append(element)
                i+=1
        else:
            html = Youtvgratis.getContentFromUrl(url=page,referer=Youtvgratis.MAIN_URL)
            logger.debug("decoded html is: "+html)
            url2 = Decoder.extractWithRegex('http://youtvgratis.com/embed/','"',html).replace('"','')
            html2 = Youtvgratis.getContentFromUrl(url=url2,referer=page,cookie=Youtvgratis.cookie)
            if 'file: "' in html2:
                listUrl = Decoder.extract('file: "','"',html2)
                if "|" in listUrl:
                    logger.debug("detected external list...")
                    listUrl = listUrl[:listUrl.find("|")]
                    newListContent = Youtvgratis.getContentFromUrl(url=listUrl)
                    if ".m3u8" in newListContent and "http" in newListContent:
                        listUrl = Decoder.extractWithRegex('http:',"=.m3u8",newListContent)
                        logger.debug("new list has been updated to: "+listUrl)
                    else:
                        logger.debug("rejected new list, using last one valid.")
                logger.debug("extracted m3u8: "+listUrl)
                element = {}
                element["link"] = listUrl
                element["title"] = page
                element["thumbnail"] = ""
                x.append(element)
            else:
                logger.debug("html2 is: "+html2)
                if 'http://cinestrenostv.tv/' in html2:
                    newUrl = Decoder.extractWithRegex('http://cinestrenostv.tv/','"',html2).replace('"',"")
                    logger.debug("extracting")
                    x = Cineestrenostv.getChannels(newUrl)
        return x

