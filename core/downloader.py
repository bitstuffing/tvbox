import urllib, httplib
from core import logger

class Downloader():

    cookie = ""

    @staticmethod
    def getContentFromUrl(url,data="",cookie="",referer="",ajax=False,launchLocation=True):
        host = url[url.find("://")+len("://"):]
        subUrl = ""
        logger.info("url is: "+host)
        if host.find("/")>-1:
            host = host[0:host.find("/")]
            subUrl = url[url.find(host)+len(host):]
        if host.find(":")==-1:
            logger.info("host: "+host+":80 , subUrl: "+subUrl)
        else:
            logger.info("host: "+host+" , subUrl: "+subUrl)
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:43.0) Gecko/20100101 Firefox/43.0",
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

        if cookie !="":
            headers["Cookie"] = cookie
        if ajax:
            headers["X-Requested-With"] = "XMLHttpRequest"
            headers["Accept"] = "*/*"
        if host.find(":")==-1:
            h = httplib.HTTPConnection(host+":80")
        else:
            h = httplib.HTTPConnection(host)
        if data == "":
            logger.info("launching GET...")
            h.request('GET', subUrl, data, headers)
        else:
            logger.info("launching POST...")
            h.request('POST', subUrl, data, headers)
        r = h.getresponse()

        headersReturned = r.getheaders()
        cfduid = ""
        location = ""
        for returnedHeader,rValue in headersReturned:
            if returnedHeader == 'set-cookie':
                #print "header1: "+returnedHeader+", value1: "+rValue
                if rValue.find("__cfduid=")>-1:
                    logger.info("detected cfduid: "+rValue)
                    cfduid = rValue[rValue.find("__cfduid="):]
                    if cfduid.find(";")>-1:
                        cfduid = cfduid[0:cfduid.find(";")]
            elif returnedHeader == 'location':
                logger.info("Location detected: using location: "+rValue)
                location = rValue
            else:
                logger.info("rejected cookie: "+returnedHeader+", "+rValue)
        if cfduid!= '':
            Downloader.cookie = cfduid
        logger.info("cookie was updated to: "+Downloader.cookie)
        html = r.read()
        if location != '' and launchLocation:
            logger.info("launching redirection to: "+location)
            html = Downloader.getContentFromUrl(location,data,Downloader.cookie,url)
        return html