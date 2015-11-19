import httplib
import urllib
import os
import binascii
from core.decoder import Decoder
from core import logger

class Zoptvcom():

    cookie = ""
    MAIN_URL = "http://www.zoptv.com"

    @staticmethod
    def getChannels(page):
        #print "original page: "+page
        #print "original page: "+page
        x = []
        oldPage = page
        if str(page) == '0':
            element = {}
            element["link"] = 'country'
            element["title"] = 'Browse by Country'
            x.append(element)
            element = {}
            element["link"] = 'genre'
            element["title"] = 'Browse by Genre'
            x.append(element)
        elif page=='country' or page=='genre':
            page=Zoptvcom.MAIN_URL
        html = ""
        if str(page) != '0':
            html = Zoptvcom.getContentFromUrl(page,"",Zoptvcom.cookie,"")
        if oldPage=='country' or oldPage=='genre':
            if oldPage == 'country':
                table = Decoder.extract('<li class="dropdown-header">Browse by Country</li>',"</ul>",html)
            else: #genre
                table = Decoder.extract('<li class="dropdown-header">Browse by Genre</li>',"</ul>",html)
            x = Zoptvcom.extractElements(table)
        else:
            if html.find('<div class="zp-channel-list">')>-1:
                #it's a list, needs decode
                table = Decoder.extract('<div class="zp-channel-list">','</a>\n</div>',html)
                x = Zoptvcom.extractElements(table)
            else:
                #print html
                while (html.find("decodeURIComponent") > -1):
                    extracted = Decoder.extract("eval(decodeURIComponent(atob('","')));",html)
                    print extracted
                    print len(extracted)
                    html = binascii.a2b_base64(extracted)
                    print html
                    print len(html)
                if html.find('var streams =[{"src":"')>-1:
                    link = Decoder.extract('var streams =[{"src":"','","',html)
                    logger.info("has been detected a link: "+link)
                    if link.find(".m3u8")==-1: #iframe
                        logger.info("extracting iframe link from: "+link)
                        html = Zoptvcom.getContentFromUrl(link,"",Zoptvcom.cookie,page)
                        print html
                        host = Decoder.extract("://","embed?",link)
                        m3u8File = Decoder.extract("var src = '","';",html)
                        if m3u8File.find("http://")==-1:
                            if m3u8File[0] == "/":
                                logger.info("converting a partial link: "+m3u8File)
                                host = Decoder.extract("://","/",link)
                            link = "http://"+host+m3u8File
                        else:
                            link = m3u8File
                        logger.info("new link is: "+link)
                    element = {}
                    element["title"] = ""
                    element["permalink"] = True
                    element["link"] = link+"|User-Agent=Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0,Cookie="+Zoptvcom.cookie+",Referer=http://www.juhe.ml/player/grindplayer/GrindPlayer.swf" #in some cases there are GET HEADERS checks, it fix issues
                    logger.info("link used will be: "+element["link"])
                    x.append(element)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        for fieldHtml in table.split(' href="'):
            if fieldHtml.find("<li>")>-1 or fieldHtml.find(' <img src="')>-1:
                element = {}
                element["link"] = Zoptvcom.MAIN_URL+fieldHtml[0:fieldHtml.find('"')]
                if fieldHtml.find(' <img src="')>-1:
                    element["title"] = Decoder.extract("<span>","</span>",fieldHtml)
                    element["thumbnail"] = Zoptvcom.MAIN_URL+Decoder.extract('<img src="','"> <span>',fieldHtml)
                    logger.info("found thumbnail: "+element["thumbnail"])
                else:
                    element["title"] = fieldHtml[fieldHtml.find('">')+2:].replace("<li>","").replace("</li>","").replace("</a>","").replace("<a","").rstrip(os.linesep)
                logger.info("found title: "+element["title"]+", link: "+element["link"])
                if len(element["title"])>0:
                    x.append(element)

        return x

    @staticmethod
    def getContentFromUrl(url,data="",cookie="",referer=""):
        form = urllib.urlencode(data)
        host = url[url.find("://")+len("://"):]
        subUrl = ""
        print "url is: "+host
        if host.find("/")>-1:
            host = host[0:host.find("/")]
            subUrl = url[url.find(host)+len(host):]
        print "host: "+host+":80 , subUrl: "+subUrl
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0",
            "Accept-Language" : "en-US,en;q=0.8,es-ES;q=0.5,es;q=0.3",
            #"Accept-Encoding" : "gzip, deflate",
            "Conection" : "keep-alive",
            "Host":host,
            "DNT":"1",
            #"Content-Type" : "application/x-www-form-urlencoded; charset=UTF-8",
            "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Host":host
        }
        if referer!="":
            headers["Referer"] = referer

        h = httplib.HTTPConnection(host+":80")
        h.request('POST', subUrl, data, headers)
        r = h.getresponse()

        headersReturned = r.getheaders()
        cfduid = ""
        location = ""
        for returnedHeader,rValue in headersReturned:
            if returnedHeader == 'set-cookie':
                #print "header1: "+returnedHeader+", value1: "+rValue
                if rValue.find("__cfduid=")>-1:
                    cfduid = rValue[rValue.find("__cfduid="):]
                    if cfduid.find(";")>-1:
                        cfduid = cfduid[0:cfduid.find(";")]
            elif returnedHeader == 'location':
                logger.info("Location detected: using location: "+rValue)
                location = rValue
            else:
                logger.info("rejected cookie: "+returnedHeader+", "+rValue)
        if cfduid!= '':
            Zoptvcom.cookie = cfduid
        logger.info("cookie was updated to: "+Zoptvcom.cookie)
        html = r.read()
        if location != '':
            logger.info("launching redirection to: "+location)
            html = Zoptvcom.getContentFromUrl(location,data,Zoptvcom.cookie,url)
        return html