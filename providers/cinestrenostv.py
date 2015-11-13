# -*- coding: utf-8 -*-

import httplib
import urllib
from core.decoder import Decoder
from core import logger

class Cineestrenostv():

    cookie = ""
    MAIN_URL = "http://cinestrenostv.tv"

    @staticmethod
    def getChannels(page):
        print "starting with page from cineestrenos section: "+page
        if str(page) == '0':
            page = Cineestrenostv.MAIN_URL+'/carrusel/tv.html'
            #page = Cineestrenostv.MAIN_URL
        html = Cineestrenostv.getContentFromUrl(page,"","",Cineestrenostv.MAIN_URL)
        x = []
        logger.info("page is: "+page)
        if page.find("/carrusel/tv.html")>-1:
            table = Decoder.extract('<div class="container">',"</div></div></div></div></div>",html)
            for fieldHtml in table.split('<div class="content">'):
                element = {}
                element["link"] = Cineestrenostv.MAIN_URL+Decoder.extract("<div><a href=\"javascript:popUp('..","')",fieldHtml)
                element["title"] = Decoder.rExtract("/",".html",element["link"])
                element["thumbnail"] = Decoder.extract(' src="','"',fieldHtml)
                logger.info("found title: "+element["title"]+", link: "+element["link"]+", thumb: "+element["thumbnail"])
                if element["thumbnail"].find("http")==0:
                    x.append(element)
        elif page == Cineestrenostv.MAIN_URL:
            table = Decoder.extract('<center><table>','</td></tr></table></center>',html)
            for fieldHtml in table.split('<td>'):
                element = {}
                element["link"] = Cineestrenostv.MAIN_URL+"/"+Decoder.extract("<a href=\"/",'"',fieldHtml)
                if element["link"].find('"')>-1:
                    element["link"] = element["link"][0:element["link"].find('"')]
                element["title"] = Decoder.extract('" title="','" target',fieldHtml)
                if element["title"].find('"')>-1:
                    element["title"] = element["title"][0:element["title"].find('"')]
                if element["title"].find(" online en directo")>-1:
                    element["title"] = element["title"][0:element["title"].find(" online")]
                if element["title"].find(" Online")>-1:
                    element["title"] = element["title"][0:element["title"].find(" Online")]
                if element["title"].find(" en directo")>-1:
                    element["title"] = element["title"][0:element["title"].find(" en directo")]
                #element["title"] = element["title"].decode('utf-8')
                element["thumbnail"] = Decoder.extract('<img src="','" height',fieldHtml)
                if element["thumbnail"].find('"')>-1:
                    element["thumbnail"] = element["thumbnail"][0:element["thumbnail"].find('"')]
                if element["thumbnail"].find("http")==0:
                    logger.info("found title: "+element["title"]+", link: "+element["link"]+", thumb: "+element["thumbnail"])
                    x.append(element)
        else:
            logger.info('extracting channel from: '+page)
            x.append(Cineestrenostv.extractChannel(html,page))
        return x

    @staticmethod
    def extractChannel(html,referer):
        element = {}
        logger.info('processing html...')
        if html.find('.php')>-1:
            logger.info("proccessing level 1, cookie: "+Cineestrenostv.cookie)
            iframeUrl = Decoder.extractWithRegex('http://','.php',html)
            if iframeUrl.find('"')>-1:
                iframeUrl = iframeUrl[0:iframeUrl.find('"')]
            html2 = Cineestrenostv.getContentFromUrl(iframeUrl,"",Cineestrenostv.cookie,referer)
            if html2.find('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="650" height="400" src="')>-1:
                element = Cineestrenostv.extractIframeChannel(html2,iframeUrl)
        elif html.find('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="650" height="500" src="')>-1:
            iframeUrl = Decoder.extract('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="650" height="500" src="','"></iframe>',html) #same case with different width and height: TODO: change to regex!!
            html2 = Cineestrenostv.getContentFromUrl(iframeUrl,"","",referer)
            if html2.find('<th scope="col"><a href="/')>-1:
                partialLink = Decoder.extract('<th scope="col"><a href="/','"><font color="ffffff">',html2)
                completeLink = Cineestrenostv.MAIN_URL+"/"+partialLink
                html3 = Cineestrenostv.getContentFromUrl(completeLink,"",Cineestrenostv.cookie,iframeUrl)
                if html3.find('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="650" height="400" src="')>-1:
                    element = Cineestrenostv.extractIframeChannel(html3,completeLink)
        return element

    @staticmethod
    def extractIframeChannel(contentHtml,referer):
        element = {}
        logger.info("proccessing level 2, cookie: "+Cineestrenostv.cookie)
        if contentHtml.find('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="653" height="403" src="')>-1:
            iframeUrl2 = Decoder.extract('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="653" height="403" src="','"></iframe>',contentHtml) #same case with different width and height: TODO: change to regex!!
        elif contentHtml.find('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="650" height="400" src="')>-1:
            iframeUrl2 = Decoder.extract('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="650" height="400" src="','"></iframe>',contentHtml) #normal cases, standar width and height
        html3 = Cineestrenostv.getContentFromUrl(iframeUrl2,"","",referer)
        if html3.find('<script type="text/javascript" src="http://tv.verdirectotv.org/channel.php?file=')>-1:
            element = Cineestrenostv.extractScriptVerdirectotv(html3,iframeUrl2)
        elif html3.find("http://www.dinostream.pw/channel.php?file=")>-1: #dinostream.pw has an iframe inside, so get iframe content and proccess it
            logger.info("proccessing level 3, cookie: "+Cineestrenostv.cookie)
            scriptUrl = Decoder.extractWithRegex("http://www.dinostream.pw/channel.php?file=",'"',html3)
            scriptUrl = scriptUrl[0:len(scriptUrl)-1]

            html4 = Cineestrenostv.getContentFromUrl(scriptUrl,"",Cineestrenostv.cookie,iframeUrl2)
            finalIframeUrl = Decoder.extractWithRegex('http://','%3D"',html4)
            finalIframeUrl = finalIframeUrl[0:len(finalIframeUrl)-1]

            logger.info("proccessing level 4, cookie: "+Cineestrenostv.cookie)

            finalHtml = Cineestrenostv.getContentFromUrl(finalIframeUrl,"",Cineestrenostv.cookie,iframeUrl2)
            #logger.info("final level5 html: "+finalHtml)
            logger.info("proccessing level 5, cookie: "+Cineestrenostv.cookie)
            playerUrl = Decoder.decodeBussinessApp(finalHtml,finalIframeUrl)
            #print "player url is: "+playerUrl
            element["title"] = "Watch streaming"
            element["permalink"] = True
            element["link"] = playerUrl
        elif html3.find("http://verdirectotv.com/tv")>-1:
            logger.info("proccessing level 3, cookie: "+Cineestrenostv.cookie)
            scriptUrl = Decoder.extractWithRegex("http://verdirectotv.com/tv",'"',html3)
            scriptUrl = scriptUrl[0:len(scriptUrl)-1]

            html4 = Cineestrenostv.getContentFromUrl(scriptUrl,"",Cineestrenostv.cookie,iframeUrl2)

            if html4.find("http://www.dinostream.pw/channel.php?file=")>-1:
                scriptUrl2 = Decoder.extractWithRegex("http://www.dinostream.pw/channel.php?file=",'&autostart=true"',html4)
                scriptUrl2 = scriptUrl2[0:len(scriptUrl2)-1]
                element = Cineestrenostv.extractDinostreamPart(scriptUrl2,scriptUrl)
            elif html4.find("<script type='text/javascript' src='http://www.embeducaster.com/static/scripts/ucaster.js'></script>")>-1: #ucaster cases
                channel = Decoder.extract("<script type='text/javascript'> width=650, height=400, channel='","'",html4)
                if html4.find('<script type="text/javascript" src="http://tv.verdirectotv.org/channel.php?file=')>-1:
                    element = Cineestrenostv.extractScriptVerdirectotv(html4,scriptUrl)
                logger.info(channel+", "+element["link"])
            elif html4.find('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="650" height="400" src="')>-1: #retry the same logic
                element = Cineestrenostv.extractIframeChannel(html4,iframeUrl2)
            elif html4.find('<script type="text/javascript" src="http://tv.verdirectotv.org/channel.php?file=')>-1:
                element = Cineestrenostv.extractScriptVerdirectotv(html4,scriptUrl)
            #else:
            #    print "big data"+html4
        elif html3.find('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="653" height="403" src="')>-1:
             #html4 = Cineestrenostv.getContentFromUrl(iframeUrl2,"","",referer)
             #if html4.find('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="653" height="403" src="')>-1:
             element = Cineestrenostv.extractIframeChannel(html3,iframeUrl2)
        elif html3.find('<iframe  src="')>-1: #special case, it's not the standard iframe
            iframeUrl3 = Decoder.extract('<iframe  src="','" name="tv" id="tv" frameborder="0" height="400" scrolling="no" width="650"></iframe>',html3)
            
        elif html3.find('file: "')>-1 and html3.find('.m3u8')>-1: #direct link, not needed any logic
            link = Decoder.extract('file: "','",',html3)
            logger.info("detected direct link: "+link)
            element["title"] = "Watching direct link"
            element["permalink"] = True
            element["link"] = link
        else: #tries to decode the bussinesslink, TODO, review this part
            playerUrl = Decoder.decodeBussinessApp(html3,iframeUrl2)
            logger.info("player url is: "+playerUrl)
            element["title"] = "Watch streaming"
            element["permalink"] = True
            element["link"] = playerUrl

        return element

    @staticmethod
    def extractScriptVerdirectotv(htmlContent,referer):
        element = {}
        logger.info("proccessing level 3, cookie: "+Cineestrenostv.cookie)
        scriptUrl = Decoder.extractWithRegex("http://tv.verdirectotv.org/channel.php?file=",'"',htmlContent)
        scriptUrl = scriptUrl[0:len(scriptUrl)-1]

        html4 = Cineestrenostv.getContentFromUrl(scriptUrl,"",Cineestrenostv.cookie,referer)
        finalIframeUrl = Decoder.extractWithRegex('http://','%3D"',html4)
        finalIframeUrl = finalIframeUrl[0:len(finalIframeUrl)-1]

        logger.info("proccessing level 4, cookie: "+Cineestrenostv.cookie)

        finalHtml = Cineestrenostv.getContentFromUrl(finalIframeUrl,"",Cineestrenostv.cookie,referer)
        #print "final level5 html: "+finalHtml
        logger.info("proccessing level 5, cookie: "+Cineestrenostv.cookie)
        playerUrl = Decoder.decodeBussinessApp(finalHtml,finalIframeUrl)
        #print "player url is: "+playerUrl
        element["title"] = "Watch streaming"
        element["permalink"] = True
        element["link"] = playerUrl

        return element

    @staticmethod
    def extractDinostreamPart(url,referer):
        element = {}
        logger.info("url: "+url+", referer: "+referer)
        html4 = Cineestrenostv.getContentFromUrl(url,"",Cineestrenostv.cookie,referer)
        finalIframeUrl = Decoder.extractWithRegex('http://','%3D"',html4)
        finalIframeUrl = finalIframeUrl[0:len(finalIframeUrl)-1]
        logger.info("proccessing level 4, cookie: "+Cineestrenostv.cookie)
        finalHtml = Cineestrenostv.getContentFromUrl(finalIframeUrl,"",Cineestrenostv.cookie,referer)
        logger.info("proccessing level 5, cookie: "+Cineestrenostv.cookie)
        playerUrl = Decoder.decodeBussinessApp(finalHtml,finalIframeUrl)
        #print "player url is: "+playerUrl
        element["title"] = "Watch streaming"
        element["permalink"] = True
        element["link"] = playerUrl

        return element

    @staticmethod
    def getContentFromUrl(url,data="",cookie="",referer=""):

        response = Decoder.getContent(url,data,referer,cookie,True)
        #logger.info(response.info())
        rValue = response.info().getheader('Set-Cookie')
        cfduid = ""
        if rValue!=None:
            logger.info("header value: "+rValue)
            if rValue.find("__cfduid=")>-1:
                cfduid = rValue[rValue.find("__cfduid="):]
                if cfduid.find(";")>-1:
                    cfduid = cfduid[0:cfduid.find(";")]
        if cfduid!= '':
            Cineestrenostv.cookie = cfduid
        html = response.read()
        return html