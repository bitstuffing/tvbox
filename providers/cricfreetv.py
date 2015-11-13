import httplib
import urllib
from core.decoder import Decoder
from core import logger

class Cricfreetv():

    cookie = ""
    MAIN_URL = "http://cricfree.tv/"

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == "0":
            html = Cricfreetv.getContentFromUrl(Cricfreetv.MAIN_URL)
            if html.find("<div id='cssmenu'>")>-1:
                cssMenu = Decoder.extract("<div id='cssmenu'>",'</a><li> </ul>',html)
                for htmlElement in cssMenu.split('<li'):
                    if htmlElement.find('<a href="')>-1:
                        element = {}
                        link = Decoder.extract('<a href="','" target="_parent"',htmlElement)
                        if htmlElement.find('<span class="channels-icon ')>-1:
                            title = Decoder.extract('<span class="channels-icon ','"></span>',htmlElement)
                        elif htmlElement.find('<span class="chclass3">')>-1:
                            title = Decoder.extract('<span class="chclass3">','</span>',htmlElement)
                        element["title"] = title
                        element["link"] = link
                        logger.info("found element: "+title+", url: "+link)
                        if title != 'ch1toch20' and title != 'No Stream':
                            x.append(element)
        else:
            response = Decoder.getContent(page)
            html = response.read()
            x.append(Cricfreetv.extractIframe(html,page))
        return x

    @staticmethod
    def extractIframe(html,referer):
        iframeUrl = Decoder.extract('<iframe frameborder="0" marginheight="0" marginwidth="0" height="555" src="','"',html)
        logger.info("level 1, iframeUrl: "+iframeUrl+", cookie: "+Cricfreetv.cookie)
        html = Cricfreetv.getContentFromUrl(iframeUrl,"",Cricfreetv.cookie,referer)
        file = Cricfreetv.seekIframeScript(html,referer,iframeUrl)
        item = {}
        item["title"] = referer
        item["link"] = file
        return item

    @staticmethod
    def launchScriptLogic(scriptRegex,html,referer,iframeUrl):
        firstScriptUrl = Decoder.extractWithRegex(scriptRegex,".js",html)
        scriptUrl = Cricfreetv.extractScriptIframeUrl(html,firstScriptUrl,referer)
        logger.info("level 2, scriptUrl: "+scriptUrl+", cookie: "+Cricfreetv.cookie)
        lastIframeHtml = Cricfreetv.getContentFromUrl(scriptUrl,"",Cricfreetv.cookie,iframeUrl)
        file = Cricfreetv.seekIframeScript(lastIframeHtml,iframeUrl,scriptUrl)
        logger.info("script logic finished!")
        return file

    @staticmethod
    def seekIframeScript(html,referer, iframeUrl):
        lastIframeHtml = html
        file = ""
        if html.find("http://theactionlive.com/live")>-1:
            file = Cricfreetv.launchScriptLogic("http://theactionlive.com/live",html,referer,iframeUrl)
        elif html.find('http://biggestplayer.me/play')>-1:
            file = Cricfreetv.launchScriptLogic("http://biggestplayer.me/play",html,referer,iframeUrl)
        elif html.find("http://www.yotv.co/play")>-1:
            file = Cricfreetv.launchScriptLogic("http://www.yotv.co/play",html,referer,iframeUrl)
        elif html.find('file: "http')>-1: #found final link
            file = Decoder.extract('file: "','"',html)
            logger.info("found final link: "+file)
        elif html.find('securetoken:')>-1:
            logger.info("building final link...")
            file = Decoder.extract('file: "','"',html)
            securetoken = Decoder.extract('securetoken: "','"',html)
            flashPlayer = 'http://p.jwpcdn.com/6/12/jwplayer.flash.swf'
            #rtmp://31.220.0.195:80/live/ playpath=eurozddd token=%Zrey(nKa@#Z swfUrl=http://p.jwpcdn.com/6/12/jwplayer.flash.swf live=1 timeout=13 pageUrl=http://reytv.co/
            rtmpUrl = file[0:file.rfind('/')+1]+" playpath="+file[file.rfind('/')+1:]+" token="+securetoken+" swfUrl=http://p.jwpcdn.com/6/12/jwplayer.flash.swf live=1 timeout=13 pageUrl="+iframeUrl
            logger.info("found final link: "+rtmpUrl)
            file = rtmpUrl
        return file

    @staticmethod
    def extractScriptIframeUrl(html,scriptUrl,referer):
        iframeUrl = ""
        scriptContent = Cricfreetv.getContentFromUrl(scriptUrl,"",Cricfreetv.cookie,referer)
        iframeUrl = Decoder.extract('src="','"',scriptContent)
        if iframeUrl.find("id='+id+'")>-1: #search id in html
            id = Decoder.extract("<script type='text/javascript'>id='","';",html)
            iframeUrl = iframeUrl[0:iframeUrl.find('?id=')+len('?id=')]+id+Cricfreetv.getWidthAndHeightParams(html)+"&stretching="
        elif iframeUrl.find("live=")>-1:
            id = Decoder.extract("<script type='text/javascript'>fid='","';",html)
            iframeUrl = iframeUrl[0:iframeUrl.find('?live=')+len('?live=')]+id+Cricfreetv.getWidthAndHeightParams(html)
        return iframeUrl

    @staticmethod
    def getWidthAndHeightParams(html):
        subUrl = ""
        if html.find("; width='")>-1:
            width = Decoder.extract("; width='","'",html)
            height = Decoder.extract("; height='","'",html)
            subUrl = "&width="+width+"&height="+height
        elif html.find("; v_height=")>-1:
            width = Decoder.extract("; v_width=",";",html)
            height = Decoder.extract("; v_height=",";",html)
            subUrl = "&vw="+width+"&vh="+height
        return subUrl

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
            Cricfreetv.cookie = cfduid
            logger.info("Cookie has been updated to: "+cfduid)
        html = response.read()
        return html