import httplib
import urllib
import os
import re
import binascii
import base64
from core.decoder import Decoder
from core import jsunpack
from core import logger
from core.downloader import Downloader

class ShowsportTvCom(Downloader):

    MAIN_URL = "http://showsport-tv.com/"

    @staticmethod
    def getChannels(page):
        x = []
        start = False
        if str(page) == '0':
            html = ShowsportTvCom.getContentFromUrl(ShowsportTvCom.MAIN_URL)
            element = {}
            element["link"] = '1'
            element["title"] = 'Display by event'
            x.append(element)
            if html.find('<div id="cssmenu">')>-1:
                cssMenu = Decoder.extract('<div id="cssmenu">','</ul>',html)
                for htmlElement in cssMenu.split('<li class="has-sub">'):
                    if htmlElement.find('<a href="')>-1:
                        element = {}
                        link = Decoder.extract('<a href="','"',htmlElement)
                        if htmlElement.find(' title="')>-1:
                            title = Decoder.extract(' title="','"',htmlElement)
                        img = Decoder.extract('img src="/','"',htmlElement)
                        element["title"] = title
                        element["link"] = ShowsportTvCom.MAIN_URL+link
                        element["thumbnail"] = ShowsportTvCom.MAIN_URL+img
                        logger.debug("found element: "+title+", url: "+element["link"])
                        if title != '':
                            x.append(element)
        elif str(page) == '1': #event
            html = ShowsportTvCom.getContentFromUrl(ShowsportTvCom.MAIN_URL)
            html = Decoder.extract('<div class="listmatch">','<div id="right_content">',html)
            for htmlElement in html.split('<div class="leaguelogo column">'):
                if htmlElement.find('<a href="')>-1:
                    href = Decoder.extract('<a href="','">',htmlElement)
                    timeHtml = Decoder.extract('<div class="date_time column"><span class="','</span></div>',htmlElement)
                    time = Decoder.extract('>','</span><span',timeHtml)
                    time+= " - "+timeHtml[timeHtml.rfind(">")+1:]
                    name = Decoder.extract('png"><span>','</span></div>',htmlElement)
                    if htmlElement.find('px;">')>-1 and htmlElement.find('</span><img')>-1:
                        name += " vs "+Decoder.extract('px;">','</span><img',htmlElement)
                    element = {}
                    element["title"] = time+" - "+name
                    element["link"] = ShowsportTvCom.MAIN_URL+href
                    x.append(element)
        else:
            html = ShowsportTvCom.getContentFromUrl(page)
            iframeUrl = ShowsportTvCom.MAIN_URL+Decoder.extract('<iframe frameborder="0" marginheight="0" marginwidth="0" height="450" src="/','"',html)
            logger.debug("iframeUrl is: "+iframeUrl)
            html2 = ShowsportTvCom.getContentFromUrl(iframeUrl,"",ShowsportTvCom.cookie,page)
            if html2.find("http://www.caston.tv/player.php?")>-1:
                id = Decoder.extract("var id = "," ;",html2)
                url2 = "http://www.caston.tv/player.php?id="+id
                html3 = ShowsportTvCom.getContentFromUrl(url2,"",ShowsportTvCom.cookie,iframeUrl)
                script = Decoder.extract('<script type="text/javascript">\n','</script>',html3)
                if script.find("document.write(unescape('")>-1: #patch
                    scriptContent = Decoder.extract("document.write(unescape('","'));",script)
                    scriptContent = urllib.unquote(scriptContent)
                    script=re.compile('eval\(function\(w,i,s,e\).*}\((.*?)\)').findall(scriptContent)[0]
                finalScriptContent = Decoder.preWise(script)
                logger.debug(finalScriptContent)
                token = Decoder.extract("token:\"","\"",finalScriptContent)
                logger.debug("pre-token is: "+token)
                ajaxContent = dict(token=token, is_ajax=1)
                tokenResponse = ShowsportTvCom.getContentFromUrl("http://www.caston.tv/ss.php",urllib.urlencode(ajaxContent),ShowsportTvCom.cookie,url2,True)
                logger.debug("token response: "+tokenResponse)
                file = Decoder.extract("file:\"","\"",finalScriptContent)+Decoder.extract('["','",',tokenResponse)
            logger.debug("final remote url: "+file)
            element = {}
            element["link"] = file
            element["permaLink"] = True
            element["title"] = "Watch streaming"
            x.append(element)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        for fieldHtml in table.split('<li>'):
            if fieldHtml.find("<a href=")>-1:
                element = {}
                element["link"] = Decoder.extract('<a href="','"',fieldHtml)
                element["title"] = Decoder.extract('alt="','">',fieldHtml)
                element["thumbnail"] = Decoder.extract('src="','" ',fieldHtml)
                logger.debug("found title: "+element["title"]+", link: "+element["link"]+", thumbnail: "+element["thumbnail"])
                if len(element["title"])>0:
                    x.append(element)
        return x