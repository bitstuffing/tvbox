# coding=utf-8
from core.xbmcutils import XBMCUtils
import urllib
from core.downloader import Downloader
from core import logger
from core.decoder import Decoder
import base64

try:
    import json
except:
    import simplejson as json


class Pepecine(Downloader):

    MAIN_URL = 'http://pepecine.net'
    SEARCH = "http://pepecine.net/ver-online?q=%s"

    @staticmethod
    def search(text):
        searchUrl = Pepecine.SEARCH % urllib.quote_plus(text)
        html = Pepecine.getContentFromUrl(url=searchUrl,referer=Pepecine.MAIN_URL,cookie=Pepecine.cookie,launchLocation=True)
        return Pepecine.extractItems(html)

    @staticmethod
    def extractItems(html):
        x = []
        htmlList = Decoder.extract('<h2 class="heading s1" style="border-radius: 10px 10px 0px 0px !important;margin-bottom: 1px !important;">','</h2>',html)
        i=0
        for htmlElement in htmlList.split("<a "):
            if i>0:
                element = {}
                title = Decoder.extract(" title=\"","\"",htmlElement)
                link = Pepecine.MAIN_URL+Decoder.extract(" href=\"", "\"", htmlElement)
                #img = Pepecine.MAIN_URL+"/"+Decoder.extract("<img src=\"","\"",htmlElement)
                element["title"] = title
                element["link"] = link
                #element["thumbnail"] = img
                x.append(element)
            i+=1
        return x

    @staticmethod
    def extractProvidersFromLink(page,providers=False):
        x = []
        token = Pepecine.getValidToken()
        logger.debug("TOKEN is: "+token)
        page2 = page % token
        bruteJson = Pepecine.getContentFromUrl(url=page2,cookie=Pepecine.cookie,referer=Pepecine.MAIN_URL)
        #logger.debug("BruteJSON is: "+bruteJson)
        totalJson = json.loads(bruteJson)
        if not providers:
            logger.debug("total items: " + str(len(totalJson["items"])))
            for elementJson in totalJson["items"]:
                element = {}
                element["thumbnail"] = elementJson["poster"]
                element["title"] = elementJson["title"].encode("utf-8")
                try:
                    element["link"] = base64.encodestring(element["title"].encode("utf-8"))
                    x.append(element)
                except:
                    logger.debug("Could not encode: "+element["title"])
                    pass
        else:
            logger.debug("using title (items should be 1 and now is: "+str(len(totalJson["items"]))+" )")
            for elementJsonBefore in totalJson["items"]:
                title = elementJsonBefore["title"].encode("utf-8")
                for elementJson in elementJsonBefore["link"]:
                    element = {}
                    element["title"] = title+" - "+elementJson["url"]
                    element["link"] = elementJson["url"]
                    element["finalLink"] = True
                    x.append(element)
        return x

    @staticmethod
    def getValidToken():
        html = Downloader.getContentFromUrl(url=Pepecine.MAIN_URL)
        token = Decoder.extract("token: '","'",html)
        return token

    @staticmethod
    def getChannels(page):
        x = []
        logger.debug("page for pepecine: "+page)
        movie = 'movie'
        serie = 'series'
        if(str(page)=="0"):
            element = {}
            element["title"] = "Películas"
            element["link"] = 'http://pepecine.net/titles/paginate?_token=%s&perPage=50&page=1&order=mc_num_of_votesDesc&type='+movie+'&minRating=&maxRating=&availToStream=true'
            x.append(element)
            element = {}
            element["title"] = "Series"
            element["link"] = 'http://pepecine.net/titles/paginate?_token=%s&perPage=50&page=1&order=mc_num_of_votesDesc&type=' + serie + '&minRating=&maxRating=&availToStream=true'
            x.append(element)
            last = {}
            last["title"] = "Últimas películas publicadas"
            last["link"] = "http://pepecine.net/plugins/ultimas-peliculas-online.php"
            x.append(last)
            last = {}
            last["title"] = "Últimas series actualizadas"
            last["link"] = "http://pepecine.net/plugins/series-episodios-online.php"
            x.append(last)
            search = {}
            search["title"] = XBMCUtils.getString(11018)
            search["link"] = ".search"
            x.append(search)

        elif page=='.search':
            logger.debug("search page detected...")
            #display keyboard, it will wait for result
            keyboard = XBMCUtils.getKeyboard()
            keyboard.doModal()
            text = ""
            if (keyboard.isConfirmed()):
                text = keyboard.getText()
                x = Pepecine.search(text)
        elif '%s' in page:
            logger.debug("list page detected...")
            x = Pepecine.extractProvidersFromLink(page)
        elif page.endswith("=") or "://" not in page:
            if "://" not in page:
                page+="=" #base64 could be missed
            title = base64.decodestring(page)
            logger.debug("trying to query by title: "+title)
            searchByTitle = "http://pepecine.net/titles/paginate?_token=%s&perPage=24&page=1&order=mc_num_of_votesDesc&type=series&minRating=&maxRating=&query="+urllib.quote_plus(title)+"&availToStream=true"
            x = Pepecine.extractProvidersFromLink(searchByTitle,True)

        return x