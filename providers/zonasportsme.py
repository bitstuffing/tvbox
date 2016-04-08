# -*- coding: utf-8 -*-

import urllib2,urlparse
import urllib
import os,re
import base64
import binascii
from core.decoder import Decoder
from core import jsunpack
from core import logger
from core.downloader import Downloader
from providers.cricfreetv import Cricfreetv

class Zonasportsme(Downloader):

    MAIN_URL = "http://zonasports.to/"

    @staticmethod
    def getChannels(page):
        x = []
        logger.debug("page is: "+page)
        if str(page) == '0':
            page=Zonasportsme.MAIN_URL
        else:
            logger.debug("decoding page: "+page)
            page = base64.b64decode(page)
            logger.debug("decoded page: "+page)
        logger.debug("launching web petition to page: "+page)
        html = Zonasportsme.getContentFromUrl(page,"",Zonasportsme.cookie,Zonasportsme.MAIN_URL)
        if page==Zonasportsme.MAIN_URL:
            logger.debug("browsing main menu...")
            menu = Decoder.extract('<ul class="nav" id="main-menu">',"</li></ul></li></ul>",html)
            x = Zonasportsme.extractElements(menu)
        else:
            #print html
            url = ""
            if html.find('var t="')>-1:
                content = Decoder.extract('var t="','";',html)
                #content = bytearray.fromhex(content).decode() #now decode hexadecima string to plain text
                try: #this fix is for an issue related to Android port
                    content = bytearray.fromhex(content).decode()
                except TypeError:  # Work-around for Python 2.6 bug
                    content = bytearray.fromhex(unicode(content)).decode()
                logger.debug("content: "+content)
                url = Decoder.extract("'file': '","'",content)
                logger.debug("found a link: "+url)
                if url.find(".m3u8")==-1:
                    logger.debug("unescape logic...")
                    extracted = Decoder.extract('document.write(unescape("','"));',html).decode('unicode-escape', 'ignore')
                    logger.debug("extracted unicode was (3 cases to be detected): "+extracted)
                    if extracted.find('file: "')>-1:
                        url = Decoder.extract('file: "','",',extracted)
                    elif extracted.find("'file': '")>-1:
                        url = Decoder.extract("'file': '","',",extracted)
                    elif extracted.find(' src="'+Zonasportsme.MAIN_URL)>-1:
                        page = Decoder.extractWithRegex(Zonasportsme.MAIN_URL,'"',extracted)
                        logger.debug("detected embed other channel, relaunching with page: \""+page)
                        return Zonasportsme.getChannels(base64.b64encode(page[:len(page)-1]))
            elif html.find("http://direct-stream.org/embedStream.js")>-1:
                iframeUrl = ""
                scriptUrl = "http://direct-stream.org/embedStream.js"
                scriptContent = Zonasportsme.getContentFromUrl(scriptUrl,"","",page)
                iframeUrl = Decoder.extract('src="','"',scriptContent)
                if iframeUrl.find("?id=")>-1:
                    if html.find('<script type="text/javascript"> fid="')>-1:
                        id = Decoder.extract('<script type="text/javascript"> fid="','";',html)
                        iframeUrl = iframeUrl[0:iframeUrl.find('?id=')+len('?id=')]+id+Cricfreetv.getWidthAndHeightParams(html)
                    else:
                        logger.debug("unescape logic...")
                        extracted = Decoder.extract('document.write(unescape("','"));',html).decode('unicode-escape', 'ignore')
                        logger.debug("extracted unicode was (no cases): "+extracted)
                        #search for .m3u8 file
                        url = Decoder.extract('file: "','",',extracted)
                else:
                    iframeUrl = Decoder.extract("<iframe src='","' ",scriptContent)
                if url == '':
                    html2 = Zonasportsme.getContentFromUrl(iframeUrl,"","",page)
                    url2 = Decoder.extract('top.location="','"',html2)#+page
                    logger.debug("using location url: "+url2)
                    #html3 = Zonasportsme.getContentFromUrl(url2,"",Zonasportsme.cookie,iframeUrl)
                    html3 = Zonasportsme.getContentFromUrl(url2,"",Zonasportsme.cookie,url2)
                    #print html3
                    swfUrl = "http://direct-stream.biz/jwplayer/jwplayer.flash.swf"
                    tcUrl = Decoder.extract('var file1 = "','";',html3)
                    playPath = tcUrl[tcUrl.rfind('/'):]
                    url = tcUrl+" swfUrl="+swfUrl+" playPath="+playPath+" live=1 pageUrl="+url2
                    logger.debug("built rtmp url: "+url)
            elif html.find("http://js.p2pcast.tech/p2pcast/player.js")>-1:
                id = Decoder.extract("<script type='text/javascript'>id='","'",html)
                newReferer = "http://p2pcast.tech/stream.php?id="+id+"&osr=0&p2p=0&stretching=uniform"
                html2 = Downloader.getContentFromUrl(newReferer,"","",page)
                html3 = Downloader.getContentFromUrl('http://p2pcast.tech/getTok.php',"","",newReferer,True)
                logger.debug("at this moment cookie is: "+Downloader.cookie)
                token = Decoder.extract('{"token":"','"}',html3)
                logger.debug("token: "+token)
                base64Url = Decoder.extract('&p2p=1&stretching=uniform&osr="</script><script>',';',html2)
                logger.debug("provisional: "+base64Url)
                base64Url = Decoder.extract('"','"',base64Url)
                url = base64.decodestring(base64Url)+token
                #logger.debug(Downloader.getContentFromUrl(url,"","","http://cdn.p2pcast.tech/jwplayer.flash.swf"))
                #fix related to token, it depends on User-Agent header content, so needs the same User-Agent in the player
                url+= "|Referer=http://cdn.p2pcast.tech/jwplayer.flash.swf&User-Agent="+"Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0".replace(" ","+")
            elif html.find("http://www.castalba.tv/js/embed.js")>-1:
                id = Decoder.extract('<script type="text/javascript"> id="','"',html)
                newUrl = "http://castalba.tv/embed.php?cid="+id+"&wh=740&ht=430&r=zonasports.to"
                url = Decoder.decodeCastalbatv(newUrl,page)
            elif html.find('src="https://streamup.com/')>-1:
                url2 = Decoder.extractWithRegex('https://streamup.com/','"',html).replace('"',"")
                html2 = Decoder.getContent(url2,"",page,"",False).read()
                channel = Decoder.extract('"roomSlug": "','"',html2)
                #response = Downloader.getContent("https://lancer.streamup.com/api/channels/"+channel+"/playlists",url2,"https://streamup.com").read()
                result = Zonasportsme.getContent("https://lancer.streamup.com/api/channels/"+channel+"/playlists", referer=url2)
                url = re.findall('.*(http[^"\']+\.m3u8[^"\']*).*',result)[0]
                #url+='|%s' %urllib.urlencode({'Referer':url2,'User-agent':client.agent()})
                swf = Decoder.extract('assetsPath: "','"',html2)+"/flashlsChromeless.swf"
                url +="|"+Downloader.getHeaders(swf)
            else:
                #http://www.byetv.org/channel.php?file=2099&width=700&height=400&autostart=true
                logger.debug("unescape logic...")
                #logger.debug(html)
                extracted = Decoder.extract('document.write(unescape("','"));',html).decode('unicode-escape', 'ignore')
                logger.debug("extracted unicode was (no cases 2): "+extracted)
                #search for .m3u8 file
                if extracted.find('file: "')>-1:
                    url = Decoder.extract('file: "','",',extracted)
                elif extracted.find('var stream = "')>-1:
                    url = Decoder.extract('var stream = "','";',extracted)
                elif extracted.find(' src="'+Zonasportsme.MAIN_URL)>-1:
                    page = Decoder.extractWithRegex(Zonasportsme.MAIN_URL,'"',extracted)
                    logger.debug("detected embed other channel, relaunching with page: \""+page)
                    return Zonasportsme.getChannels(base64.b64encode(page[:len(page)-1])) ##TODO, remake this part because there are some links that could not being working
            element = {}
            element["title"] = "Stream"
            element["link"] = url
            element["permaLink"] = True
            x.append(element)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        i = 0
        for value in table.split('<li>'):
            logger.debug("loop: "+str(i))
            if i>0:
                element = {}
                title = Decoder.extract(">",'</a></li>',value)
                link = Decoder.extract("href=\"",'"',value)
                element["title"] = title
                element["link"] = base64.b64encode(str(Zonasportsme.MAIN_URL+link))
                logger.debug("append: "+title+", link: "+element["link"])
                x.append(element)
            i+=1
        return x

    @staticmethod
    def getContent(url, referer="",proxy=None, post=None):
        timeout='14'
        result = ""
        headers = {}
        try:
            handlers = []
            handlers += [urllib2.ProxyHandler({'http':'%s'%(proxy)}),urllib2.HTTPHandler]
            opener = urllib2.build_opener(*handlers)
            opener = urllib2.install_opener(opener)
            headers['User-Agent'] = Downloader.USER_AGENT
            if referer != "":
                headers['referer'] = referer
            headers['Accept-Language'] = 'en-US'
            request = urllib2.Request(url, data=post, headers=headers)
            try:
                response = urllib2.urlopen(request, timeout=int(timeout))
            except urllib2.HTTPError as response:
                pass
            result = response.read(1024 * 1024) #without buffer sometimes it does not work :'(
            response.close()
        except:
            logger.error("something wrong happened with this url: "+url)
        return result