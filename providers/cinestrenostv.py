# -*- coding: utf-8 -*-

import httplib
import urllib
import os,sys
import xbmcplugin
from core.decoder import Decoder
from core import logger
from core.downloader import Downloader

class Cineestrenostv(Downloader):

    MAIN_URL = "http://cinestrenostv.tv"

    @staticmethod
    def getChannels(page):
        logger.debug("starting with page from cineestrenos section: "+page)
        if str(page) == '0':
            tradicionalChannels = xbmcplugin.getSetting(int(sys.argv[1]), "extended_channels")
            logger.debug("using carrusel: "+str(tradicionalChannels))
            if tradicionalChannels=="false":
                page = Cineestrenostv.MAIN_URL+'/carrusel/tv.html'
            else:
                page = Cineestrenostv.MAIN_URL
        html = Cineestrenostv.getContentFromUrl(page,"","",Cineestrenostv.MAIN_URL)
        x = []
        logger.debug("page is: "+page)
        if page.find("/carrusel/tv.html")>-1:
            table = Decoder.extract('<div class="container">',"</div></div></div></div></div>",html)
            for fieldHtml in table.split('<div class="content">'):
                element = {}
                element["link"] = Cineestrenostv.MAIN_URL+Decoder.extract("<div><a href=\"javascript:popUp('..","')",fieldHtml)
                if element["link"].find('/multi')!=-1:
                    logger.debug("found multi link: "+element["link"])
                    element["title"] = Decoder.extract("/multi","/",element["link"])
                else:
                    element["title"] = Decoder.rExtract("/",".html",element["link"])
                    if element["title"].find(".")>-1:
                        element["title"] = element["title"][:element["title"].rfind(".")]
                element["thumbnail"] = Decoder.extract(' src="','"',fieldHtml)
                element["title"] = element["title"].replace("-"," ")
                logger.debug("found title: "+element["title"]+", link: "+element["link"]+", thumb: "+element["thumbnail"])
                if element["thumbnail"].find("http")==0 and not(element["title"]=="1" or element["title"]=="venus"):
                    x.append(element)
        elif page == Cineestrenostv.MAIN_URL:
            table = Decoder.extract('<center><table>','</td></tr></table></center>',html)
            for fieldHtml in table.split('<td>'):
                element = {}
                element["link"] = Cineestrenostv.MAIN_URL+"/"+Decoder.extract("<a href=\"/",'"',fieldHtml)
                if element["link"].find('"')>-1:
                    element["link"] = element["link"][0:element["link"].find('"')]
                if element["link"].find('/multi')!=-1:
                    logger.debug("found multi link: "+element["link"])
                    element["title"] = Decoder.extract("/multi","/",element["link"])
                else:
                    logger.debug("found normal link, continue... "+ element["link"])
                    element["title"] = Decoder.extract('" title="','" target',fieldHtml)
                    if element["title"].find('"')>-1:
                        element["title"] = element["title"][0:element["title"].find('"')]
                    if element["title"].find(" online")>-1:
                        element["title"] = element["title"][0:element["title"].find(" online")]
                    if element["title"].find(" Online")>-1:
                        element["title"] = element["title"][0:element["title"].find(" Online")]
                    if element["title"].find(" en directo")>-1:
                        element["title"] = element["title"][0:element["title"].find(" en directo")]

                    element["title"] = element["title"].replace("ver ","")

                #element["title"] = element["title"].decode('utf-8')
                element["thumbnail"] = Decoder.extract('<img src="','" height',fieldHtml)
                if element["thumbnail"].find('"')>-1:
                    element["thumbnail"] = element["thumbnail"][0:element["thumbnail"].find('"')]
                if element["thumbnail"].find("http")==0:
                    logger.debug("found title: "+element["title"]+", link: "+element["link"]+", thumb: "+element["thumbnail"])
                    if element["thumbnail"].find("http")==0 and not(element["title"]=="1" or element["title"]=="gran hermano mexico" or element["title"]=="alx syfy" or element["title"]=="intereconomia punto pelota" or element["title"]=="cine" or element["title"].find("-LATINOAMERICA")>-1):
                        x.append(element)
        else:
            logger.debug('extracting channel from: '+page)
            x.append(Cineestrenostv.extractChannel(html,page))
        return x

    @staticmethod
    def extractChannel(html,referer):
        element = {}
        logger.debug('processing html...')
        if html.find('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="650" height="400" src="')>-1:
            element = Cineestrenostv.extractIframeChannel(html,referer)
        elif html.find('.php')>-1 and referer.find(".php")==-1:
            logger.debug("proccessing level 1, cookie: "+Cineestrenostv.cookie)
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
        elif referer.find("php")!=-1:
            referer = referer.replace("ñ","%C3%B1")
            html2 = Cineestrenostv.getContentFromUrl(referer,"",Cineestrenostv.cookie,referer)
            element = Cineestrenostv.extractIframeChannel(html2,referer)
        return element

    @staticmethod
    def extractIframeChannel(contentHtml,referer):
        logger.debug("proccessing level 2, cookie: "+Cineestrenostv.cookie)
        iframeUrl2 = "dummy url"
        if contentHtml.find('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="653" height="403" src="')>-1:
            iframeUrl2 = Decoder.extract('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="653" height="403" src="','"></iframe>',contentHtml).replace("ñ","%C3%B1") #same case with different width and height: TODO: change to regex!!
        elif contentHtml.find('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="650" height="400" src="')>-1:
            iframeUrl2 = Decoder.extract('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="650" height="400" src="','"></iframe>',contentHtml).replace("ñ","%C3%B1") #normal cases, standar width and height
        if iframeUrl2!="dummy url":
            html3 = Cineestrenostv.getContentFromUrl(iframeUrl2,"","",referer)
            return Cineestrenostv.mainLogicExtractIframeChannel(html3,iframeUrl2)
        else:
            return Cineestrenostv.mainLogicExtractIframeChannel(contentHtml,referer)

    @staticmethod
    def mainLogicExtractIframeChannel(html3,iframeUrl2):
        element = {}
        if html3.find('<script type="text/javascript" src="http://tv.verdirectotv.org/channel.php?file=')>-1:
            element = Cineestrenostv.extractScriptVerdirectotv(html3,iframeUrl2)
        elif html3.find("http://vercanalestv.com/tv/")>-1: #vercanalestv
            iframeUrl = Decoder.extractWithRegex("http://vercanalestv.com/tv/",'"',html3)
            logger.debug("obtained iframeUrl: "+iframeUrl)
            html2 = Cineestrenostv.getContentFromUrl(iframeUrl[0:len(iframeUrl)-1],"",Cineestrenostv.cookie,"")
            if html2.find('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="650" height="400" src="')>-1:
                element = Cineestrenostv.extractIframeChannel(html2,iframeUrl)
            else:
                logger.error("Something unexpected happened with url: "+iframeUrl)
                #print "ERROR: "+html2
        elif html3.find("http://www.dinostream.pw/channel.php?file=")>-1: #dinostream.pw has an iframe inside, so get iframe content and proccess it
            logger.debug("proccessing level 3, cookie: "+Cineestrenostv.cookie)
            scriptUrl = Decoder.extractWithRegex("http://www.dinostream.pw/channel.php?file=",'"',html3)
            scriptUrl = scriptUrl[0:len(scriptUrl)-1]

            html4 = Cineestrenostv.getContentFromUrl(scriptUrl,"",Cineestrenostv.cookie,iframeUrl2)
            finalIframeUrl = Decoder.extractWithRegex('http://','%3D"',html4)
            finalIframeUrl = finalIframeUrl[0:len(finalIframeUrl)-1]

            logger.debug("proccessing level 4, cookie: "+Cineestrenostv.cookie)

            finalHtml = Cineestrenostv.getContentFromUrl(finalIframeUrl,"",Cineestrenostv.cookie,iframeUrl2)
            #logger.debug("final level5 html: "+finalHtml)
            logger.debug("proccessing level 5, cookie: "+Cineestrenostv.cookie)
            playerUrl = Decoder.decodeBussinessApp(finalHtml,finalIframeUrl)
            #print "player url is: "+playerUrl
            element["title"] = "Watch streaming"
            element["permalink"] = True
            element["link"] = playerUrl
        elif html3.find("<script type='text/javascript' src='http://www.embeducaster.com/static/scripts/ucaster.js'></script>")>-1: #ucaster cases
            if html3.find("<script type='text/javascript'> width=650, height=400, channel='")>-1:
                channel = Decoder.extract("<script type='text/javascript'> width=650, height=400, channel='","'",html3)
            else:
                channel = Decoder.extract("<script type='text/javascript'> width=","',",html3)
                channel = channel[channel.find("channel='")+len("channel='"):]
            logger.debug("ucaster channel: "+channel)
            if html3.find('<script type="text/javascript" src="http://tv.verdirectotv.org/channel.php?file=')>-1:
                element = Cineestrenostv.extractScriptVerdirectotv(html3,iframeUrl2)
            else:
                ucasterUrl = 'http://www.embeducaster.com/embedplayer/'+channel+'/1/620/430'
                html4 = Cineestrenostv.getContentFromUrl(ucasterUrl,"",Cineestrenostv.cookie,iframeUrl2)
                playerUrl = Decoder.decodeUcaster(html4,iframeUrl2)
                logger.debug("lifeflash - player url is: "+playerUrl)
                element["title"] = "Watch streaming"
                element["permalink"] = True
                element["link"] = playerUrl
            logger.debug(channel+", "+element["link"])
        elif html3.find('http://www.mipsplayer.com/content/scripts/mipsEmbed.js')>-1: #before verdirectotv.com, if not is always called
            channel = Decoder.extract("channel='","'",html3)
            mipsUrl = 'http://www.mipsplayer.com/embedplayer/'+channel+'/1/650/400'
            logger.debug("mips url is: "+mipsUrl)
            html4 = Cineestrenostv.getContentFromUrl(mipsUrl,"",Cineestrenostv.cookie,iframeUrl2)
            playerUrl = Decoder.decodeMipsplayer(html4,iframeUrl2)
            logger.debug("mipsplayer - player url is: "+playerUrl)
            element["title"] = "Watch streaming"
            element["permalink"] = True
            element["link"] = playerUrl
        elif html3.find("http://verdirectotv.com/tv")>-1:
            logger.debug("proccessing level 3, cookie: "+Cineestrenostv.cookie)
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
                else:
                    ucasterUrl = 'http://www.embeducaster.com/embedplayer/'+channel+'/1/620/430'
                    html4 = Cineestrenostv.getContentFromUrl(ucasterUrl,"",Cineestrenostv.cookie,scriptUrl)
                    playerUrl = Decoder.decodeUcaster(html4,iframeUrl2)
                    logger.debug("lifeflash - player url is: "+playerUrl)
                    element["title"] = "Watch streaming"
                    element["permalink"] = True
                    element["link"] = playerUrl
                logger.debug(channel+", "+element["link"])
            elif html4.find('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="650" height="400" src="')>-1: #retry the same logic
                element = Cineestrenostv.extractIframeChannel(html4,iframeUrl2)
            elif html4.find('<script type="text/javascript" src="http://tv.verdirectotv.org/channel.php?file=')>-1:
                element = Cineestrenostv.extractScriptVerdirectotv(html4,scriptUrl)
            elif html4.find("<script type='text/javascript' src='http://www.liveflashplayer.net/resources/scripts/")>-1:
                channel = Decoder.extract("channel='","'",html4)
                mipsUrl = 'http://www.liveflashplayer.net/embedplayer/'+channel+'/1/620/430'
                html4 = Cineestrenostv.getContentFromUrl(mipsUrl,"",Cineestrenostv.cookie,scriptUrl)
                playerUrl = Decoder.decodeLiveFlash(html4,iframeUrl2)
                logger.debug("lifeflash - player url is: "+playerUrl)
                element["title"] = "Watch streaming"
                element["permalink"] = True
                element["link"] = playerUrl
            elif html4.find('http://www.mipsplayer.com/content/scripts/mipsEmbed.js')>-1:
                channel = Decoder.extract("channel='","'",html4)
                mipsUrl = 'http://www.mipsplayer.com/embedplayer/'+channel+'/1/650/400'
                html4 = Cineestrenostv.getContentFromUrl(mipsUrl,"",Cineestrenostv.cookie,scriptUrl)
                playerUrl = Decoder.decodeMipsplayer(html4,iframeUrl2)
                logger.debug("mipsplayer - player url is: "+playerUrl)
                element["title"] = "Watch streaming"
                element["permalink"] = True
                element["link"] = playerUrl
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
            link = link+"|Referer="+iframeUrl2
            logger.debug("detected direct link: "+link)
            element["title"] = "Watching direct link"
            element["permalink"] = True
            element["link"] = link
        elif html3.find("http://telefivegb.com/")>-1 or html3.find("http://verlatelegratis.net")>-1:
            element = Cineestrenostv.extractNewIframeChannel(html3,iframeUrl2)
        elif html3.find("http://tvpor-internet.com/")>-1 or html3.find("http://www.malosolandia.com/")>-1:
            logger.debug("inside here!..")
            newUrl = "dummy url" #dummy
            if html3.find("http://tvpor-internet.com/")>-1:
                logger.debug("inside here1!..")
                newUrl = Decoder.extractWithRegex('http://tvpor-internet.com/','"',html3).replace('"',"")
            elif html3.find("http://www.malosolandia.com/")>-1:
                logger.debug("inside here2!..")
                logger.debug("using malosolandia")
                newUrl = Decoder.extractWithRegex('http://www.malosolandia.com/','.html',html3)
            else:
                logger.debug("nothing done!")
            if newUrl!="dummy url":
                logger.debug("html is: "+html3)
                logger.debug("using new url: "+newUrl)
                html4 = Cineestrenostv.getContentFromUrl(newUrl,"",Cineestrenostv.cookie,iframeUrl2)
                logger.debug("redirecting using: "+newUrl+", html: "+html4)
                element = Cineestrenostv.mainLogicExtractIframeChannel(html4,newUrl)
            else:
                logger.debug(html3)
        elif html3.find("http://www.rtve.es/directo/la-2/")>-1:
            element["title"] = "Watch streaming"
            element["permalink"] = True
            element["link"] = "http://hlslive.rtve.es/LA2_LV3_IPH/LA2_LV3_IPH.m3u8"
        elif html3.find("http://www.rtve.es/directo/canal-24h/")>-1:
            element["title"] = "Watch streaming"
            element["permalink"] = True
            element["link"] = "http://hlslive.rtve.es/24H_LV3_IPH/24H_LV3_IPH.m3u8"
        elif html3.find("http://leton.tv/player.php")>-1:
            logger.debug("detected leton link...")
            letonUrl = Decoder.extractWithRegex('http://leton.tv/player.php','"',html3).replace('"',"")
            letonHtml = Cineestrenostv.getContentFromUrl(letonUrl,"",Cineestrenostv.cookie,iframeUrl2)
            #print letonHtml
            playerUrl = Decoder.decodeLetonTv(letonHtml,letonUrl)
            element["title"] = "Watch streaming"
            element["permalink"] = True
            element["link"] = playerUrl
        elif html3.find('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="650" height="400" src="')>-1:
            logger.debug("detected iframe with embed page, doing a new loop again...")
            iframeUrl3 = Decoder.extract('<iframe scrolling="no" marginwidth="0" marginheight="0" frameborder="0" width="650" height="400" src="','"></iframe>',html3) #normal cases, standar width and height
            if iframeUrl3!=iframeUrl2:
                html4 = Cineestrenostv.getContentFromUrl(iframeUrl3,"","",iframeUrl2)
                return Cineestrenostv.mainLogicExtractIframeChannel(html4,iframeUrl3)
            else:
                logger.debug("infinite loop detected, stopped!")
        else: #tries to decode the bussinesslink, TODO, review this part
            #print html3
            playerUrl = Decoder.decodeBussinessApp(html3,iframeUrl2)
            logger.debug("bussinessapp - player url is: "+playerUrl)
            element["title"] = "Watch streaming"
            element["permalink"] = True
            element["link"] = playerUrl
        return element

    @staticmethod
    def extractNewIframeChannel(html3,iframeUrl2):
        element = {}
        if html3.find("http://telefivegb.com/")>-1:
            logger.debug("found telefivegb.com link, using that link to...")
            newUrl = Decoder.extractWithRegex('http://telefivegb.com/','"',html3).replace('"',"")
        elif html3.find("http://verlatelegratis.net")>-1:
            logger.debug("found verlatelegratis.net link, using that link to...")
            newUrl = Decoder.extractWithRegex('http://verlatelegratis.net','"',html3).replace('"',"")
        html4 = Cineestrenostv.getContentFromUrl(newUrl,"",Cineestrenostv.cookie,iframeUrl2)
        if html4.find("http://www.playerhd1.pw/")>-1:
            logger.debug("found playerhd1.pw, using that link, continue...")
            scriptUrl = Decoder.extractWithRegex("http://www.playerhd1.pw/",'"',html4).replace('"',"")

            html4 = Cineestrenostv.getContentFromUrl(scriptUrl,"",Cineestrenostv.cookie,newUrl)

            finalIframeUrl = Decoder.extractWithRegex('http://','%3D"',html4)
            finalIframeUrl = finalIframeUrl[0:len(finalIframeUrl)-1]

            logger.debug("proccessing level 4, cookie: "+Cineestrenostv.cookie)

            finalHtml = Cineestrenostv.getContentFromUrl(finalIframeUrl,"",Cineestrenostv.cookie,newUrl)
            #print "final level5 html: "+finalHtml
            logger.debug("proccessing level 5, cookie: "+Cineestrenostv.cookie)
            playerUrl = Decoder.decodeBussinessApp(finalHtml,finalIframeUrl)

            #print "player url is: "+playerUrl
            element["title"] = "Watch streaming"
            element["permalink"] = True
            element["link"] = playerUrl
        else:
            logger.debug("possible redirect to his domains: "+html4+", try again..."+newUrl)
            #element = Cineestrenostv.extractIframeChannel(html4,newUrl)
            element = Cineestrenostv.extractNewIframeChannel(html4,newUrl)
        return element

    @staticmethod
    def extractScriptVerdirectotv(htmlContent,referer):
        element = {}
        logger.debug("proccessing level 3, cookie: "+Cineestrenostv.cookie)
        scriptUrl = Decoder.extractWithRegex("http://tv.verdirectotv.org/channel.php?file=",'"',htmlContent)
        scriptUrl = scriptUrl[0:len(scriptUrl)-1]

        html4 = Cineestrenostv.getContentFromUrl(scriptUrl,"",Cineestrenostv.cookie,referer)
        finalIframeUrl = Decoder.extractWithRegex('http://','%3D"',html4)
        finalIframeUrl = finalIframeUrl[0:len(finalIframeUrl)-1]

        logger.debug("proccessing level 4, cookie: "+Cineestrenostv.cookie)

        finalHtml = Cineestrenostv.getContentFromUrl(finalIframeUrl,"",Cineestrenostv.cookie,referer)
        #print "final level5 html: "+finalHtml
        logger.debug("proccessing level 5, cookie: "+Cineestrenostv.cookie)
        playerUrl = Decoder.decodeBussinessApp(finalHtml,finalIframeUrl)
        #print "player url is: "+playerUrl
        element["title"] = "Watch streaming"
        element["permalink"] = True
        element["link"] = playerUrl

        return element

    @staticmethod
    def extractDinostreamPart(url,referer):
        element = {}
        logger.debug("url: "+url+", referer: "+referer)
        html4 = Cineestrenostv.getContentFromUrl(url,"",Cineestrenostv.cookie,referer)
        finalIframeUrl = Decoder.extractWithRegex('http://','%3D"',html4)
        finalIframeUrl = finalIframeUrl[0:len(finalIframeUrl)-1]
        logger.debug("proccessing level 4, cookie: "+Cineestrenostv.cookie)
        finalHtml = Cineestrenostv.getContentFromUrl(finalIframeUrl,"",Cineestrenostv.cookie,referer)
        logger.debug("proccessing level 5, cookie: "+Cineestrenostv.cookie)
        playerUrl = Decoder.decodeBussinessApp(finalHtml,finalIframeUrl)
        #print "player url is: "+playerUrl
        element["title"] = "Watch streaming"
        element["permalink"] = True
        element["link"] = playerUrl

        return element