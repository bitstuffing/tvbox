from core.decoder import Decoder
from core import jsunpack
from core import logger
from core.downloader import Downloader

class Mamahdcom(Downloader):

    MAIN_URL = "http://mamahd.com/"

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == '0':
            html = Mamahdcom.getContentFromUrl(Mamahdcom.MAIN_URL,"",Mamahdcom.cookie,"")
        else:
            html = Mamahdcom.getContentFromUrl(page,"",Mamahdcom.cookie,"")
        #print html
        if page=='0': #menu
            table = Decoder.extract('<div class="standard row channels">','</div>',html)
            x = Mamahdcom.extractElements(table)
            logger.debug("live9 channels logic done!")
        else:
            iframeHtml = Decoder.extract("<iframe ","</iframe>",html)
            iframeUrl = Decoder.extract('src="','"',iframeHtml)
            html2 = Mamahdcom.getContentFromUrl(iframeUrl,"",Mamahdcom.cookie,page)
            #print html2
            if html2.find('src="http://hdcast.org/')>-1:
                scriptUrl = Decoder.extract('<script type="text/javascript" src="','"></script>',html2)
                iframeUrl2 = Mamahdcom.extractScriptIframeUrl(html2,scriptUrl,iframeUrl)
                finalRtmpUrl = Mamahdcom.extractFinalRtmpUrl(iframeUrl2,iframeUrl)
                element = {}
                element["link"] = finalRtmpUrl
                element["title"] = "Watch channel"
                element["permaLink"] = True
                logger.debug("finished append element!")
                x.append(element)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        for fieldHtml in table.split('</a>'):
            if fieldHtml.find("<a href=")>-1:
                element = {}
                element["link"] = Decoder.extract('<a href="','"',fieldHtml)
                element["title"] = Decoder.extract("<br><span>","</span>",fieldHtml)
                element["thumbnail"] = Decoder.extract('<img src="','"',fieldHtml)
                element["permaLink"] = True
                logger.debug("found title: "+element["title"]+", link: "+element["link"]+", thumb: "+element["thumbnail"])
                if len(element["title"])>0:
                    x.append(element)

        return x


    @staticmethod
    def extractScriptIframeUrl(html,scriptUrl,referer):
        iframeUrl = ""
        scriptContent = Mamahdcom.getContentFromUrl(scriptUrl,"",Mamahdcom.cookie,referer)
        #print scriptContent
        iframeUrl = Decoder.extract('src="',"'",scriptContent)
        logger.debug("brute iframeUrl is: "+iframeUrl)
        if iframeUrl.find("?u=")>-1:
            if html.find('<script type="text/javascript"> fid="')>-1:
                id = Decoder.extract('<script type="text/javascript"> fid="',"\";",html)
            iframeUrl = iframeUrl+id+Mamahdcom.getWidthAndHeightParams(html)
        return iframeUrl

    @staticmethod
    def getWidthAndHeightParams(html):
        subUrl = ""
        if html.find("; v_width=")>-1:
            width = Decoder.extract("; v_width=",";",html)
            height = Decoder.extract("; v_height=",";",html)
            subUrl = "&vw="+width+"&vh="+height
            logger.debug("width-height subUrl now is: "+subUrl)
        return subUrl

    @staticmethod
    def extractFinalRtmpUrl(url,referer):
        rtmpUrl = ""
        html = Mamahdcom.getContentFromUrl(url,"",Mamahdcom.cookie,referer)
        file = Decoder.extract("file:'",'\',',html)
        rtmp = file[0:file.rfind("/")+1]
        playpath = file[file.rfind("/")+1:]
        swfUrl = ""
        secureToken = "SECURET0KEN#yw%.?()@W!"
        if url.find("hdcast.org")>-1:
            swfUrl = "http://player.hdcast.org/jws/jwplayer.flash.swf"
        rtmpUrl = rtmp+" playPath="+playpath+" swfUrl="+swfUrl+" pageUrl="+url+" flashver=WIN/2019,0,0,226 live=true timeout=14 token="+secureToken
        logger.debug("built final rtmp link: "+rtmpUrl)
        return rtmpUrl