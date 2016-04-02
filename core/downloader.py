import urllib, urllib2, httplib
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
            logger.debug("host: "+host+":80 , subUrl: "+subUrl)
        else:
            logger.debug("host: "+host+" , subUrl: "+subUrl)
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
            logger.debug("launching GET...")
            h.request('GET', subUrl, data, headers)
            r = h.getresponse()
            headersReturned = r.getheaders()
            cfduid = ""
            location = ""
            for returnedHeader,rValue in headersReturned:
                if returnedHeader == 'set-cookie':
                    #print "header1: "+returnedHeader+", value1: "+rValue
                    if rValue.find("__cfduid=")>-1:
                        logger.debug("detected cfduid: "+rValue)
                        cfduid = rValue[rValue.find("__cfduid="):]
                        if cfduid.find(";")>-1:
                            cfduid = cfduid[0:cfduid.find(";")]
                elif returnedHeader == 'location':
                    logger.info("Location detected: using location: "+rValue)
                    location = rValue
                else:
                    logger.debug("rejected cookie: "+returnedHeader+", "+rValue)
            if cfduid!= '':
                Downloader.cookie = cfduid
            logger.info("cookie was updated to: "+Downloader.cookie)
            html = r.read()
            if location != '' and launchLocation:
                if location=="/":
                    location = url
                elif location.find("/")==0:
                    location = "http://"+host+location
                logger.info("launching redirection to: "+location)
                html = Downloader.getContentFromUrl(location,data,Downloader.cookie,url)
        else:
            logger.debug("launching POST...")
            req = urllib2.Request(url, data, headers)
            r = urllib2.urlopen(req)
            logger.debug(str(r.info()))
            cookie = ""
            html = r.read()
            #update cookies
            for key1, value1 in sorted(r.info().items()):
                logger.debug("trace....."+key1)
                if key1.lower()=='set-cookie':
                    value1 = value1.replace("path=/, ","")
                    if value1.find(";")==-1:
                        value1+=";="
                    logger.debug("processing cookie...: "+value1)
                    if value1.find(";")>-1:
                        for values in value1.split(";"):
                            logger.debug(values)
                            if values.find("=")>-1:
                                key = values.split("=")[0]
                                value = values.split("=")[1]
                                logger.debug("key: "+key+", value="+value)
                                if(key.find("PHPSESSID")>-1 or key.find("captcha_keystring")>-1 or key.find("__cfduid")>-1 or key.find("key")):
                                    if value.find(";")>-1:
                                        cookie+=key+"="+value[:value.find(";")]
                                    else:
                                        cookie+=key+"="+value
                                    cookie+=";"
                                    logger.debug("processed cookie: "+key+"="+value)
                else:
                    logger.debug("rejected cookie: "+key1+"->"+value1)
            if len(cookie)>1:
                Downloader.cookie = cookie
                logger.info("Cookie was updated to: "+cookie)
        return html