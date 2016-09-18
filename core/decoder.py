#-*- coding: utf-8 -*-
import httplib
import urllib2
import urllib
import time
import random
import sys
import re
import base64
import urlparse
from core import logger
from core.downloader import Downloader
try:
    import json
except:
    import simplejson as json
from core import jsunpack
from core import jsunpackOld
from core.xbmcutils import XBMCUtils

class Decoder():

    @staticmethod
    def decodeLink(link,referer=''):
        if link.find("http://streamcloud.")>-1 :
            link = Decoder.decodeStreamcloud(link)
        elif link.find("http://powvideo.net")>-1:
            link = Decoder.decodePowvideo(link)
        elif link.find("http://www.flashx.tv")>-1:
            link = Decoder.decodeFlashx(link)
        elif link.find("http://www.nowvideo.sx")>-1:
            link = Decoder.decodeNowvideo(link)
        elif link.find("http://gamovideo.")>-1:
            link = Decoder.decodeGamovideo(link)
        elif link.find("http://streamin.")>-1:
            link = Decoder.decodeStreamin(link)
        elif link.find("http://thevideo.me")>-1:
            link = Decoder.decodeThevideo(link)
        elif link.find("http://streamplay.to")>-1:
            link = Decoder.decodeStreamplay(link)
        elif link.find("http://vidxtreme.to")>-1:
            link = Decoder.decodeVidXtreme(link)
        elif link.find("http://streame.net")>-1:
            link = Decoder.decodeStreame(link)
        elif link.find("://openload")>-1 and link.find("/stream/")==-1:
            try:
                link = Decoder.decodeOpenloadUsingOfficialApi(link)
            except:
                logger.error("API doesn't work fine, so it's used the web method")
                link = Decoder.decodeOpenload(link)
        elif link.find("://idowatch.net/")>-1:
            link = Decoder.decodeIdowatch(link)
        elif link.find("://vid.ag/")>-1:
            link = Decoder.decodeVidag(link)
        elif link.find("://letwatch.us/")>-1:
            link = Decoder.decodeLetwatch(link)
        elif link.find("://bestreams.net")>-1:
            link = Decoder.decodeBestreams(link)
        elif link.find("http://www.vidgg.to/")>-1 or link.find("http://www.vid.gg/")>-1:
            link = Decoder.decodeVidggTo(link)
        elif link.find("http")==0 and link.find("video.streamable.ch/")==-1 and link.find("streamable.ch")>-1:
            link = Decoder.decodeStreamable(link)
        elif link.find('http://www.streamlive.to/embed/')>-1:
            link = Decoder.decodeStreamliveto(link,'http://www.streamlive.to')
        elif link.find("http://castalba.tv/")>-1:
            link = Decoder.decodeCastalbatv(link,referer)
        elif link.find("http://www.dinostream.pw/")>-1:
            link = Decoder.extractDinostreamPart(link)["link"]
        elif link.find("http://www.iguide.to/embed")>-1:
            link = Decoder.decodeIguide(link)
        elif 'http://hdfull.tv/ext/' in link:
            linkToDecode = link[link.rfind('/')+1:]
            logger.debug("link to decode: " + linkToDecode)
            linkDecoded = base64.decodestring(linkToDecode)
            logger.debug("Launched process to decode link: "+linkDecoded)
            link = Decoder.decodeLink(linkDecoded)
        elif "youtube." in link:
            from providers.youtube import Youtube
            link = Youtube.extractTargetVideo(link)
        return link

    @staticmethod
    def downloadY(video_id):
        listUrls = []
        response = urllib2.urlopen("http://www.youtube.com/get_video_info?video_id=" + video_id)
        data = response.read()
        logger.debug(data)
        info = urlparse.parse_qs(data)
        title = info['title'][0]
        logger.debug("youtube title: " + title)
        stream_map = info['url_encoded_fmt_stream_map'][0]
        video_info = stream_map.split(",")
        for video in video_info:
            item = urlparse.parse_qs(video)
            # print item['quality'][0]
            # print item['type'][0]
            # print item['url'][0]
            url = item['url'][0]
            logger.debug("quality is: " + item['quality'][0])
            logger.debug("url at this moment is (youtube): " + url)
            listUrls.append(url)
        return listUrls[0]

    @staticmethod
    def extractDinostreamPart(url,referer=''):
        element = {}
        logger.debug("url: "+url+", referer: "+referer)
        html4 = Downloader.getContentFromUrl(url,"","",referer)
        finalIframeUrl = Decoder.extractWithRegex('http://','%3D"',html4)
        finalIframeUrl = finalIframeUrl[0:len(finalIframeUrl)-1]
        logger.debug("proccessing level 4, cookie: "+Downloader.cookie)
        finalHtml = Downloader.getContentFromUrl(finalIframeUrl,"",Downloader.cookie,referer)
        logger.debug("proccessing level 5, cookie: "+Downloader.cookie)
        playerUrl = Decoder.decodeBussinessApp(finalHtml,finalIframeUrl)
        element["title"] = "Watch streaming"
        element["permalink"] = True
        element["link"] = playerUrl

        return element

    @staticmethod
    def extract(fromString,toString,data):
        newData = data[data.find(fromString)+len(fromString):]
        newData = newData[0:newData.find(toString)]
        return newData

    @staticmethod
    def rExtract(fromString,toString,data):
        newData = data[0:data.rfind(toString)]
        newData = newData[newData.rfind(fromString)+len(fromString):]
        return newData

    @staticmethod
    def extractWithRegex(fromString,toString,data):
        newData = data[data.find(fromString):]
        newData = newData[0:newData.find(toString)+len(toString)]
        return newData

    @staticmethod
    def rExtractWithRegex(fromString,toString,data):
        newData = data[0:data.rfind(toString)+len(toString)]
        newData = newData[newData.rfind(fromString):]

        return newData

    @staticmethod
    def getFinalHtmlFromLink(link,waitTime=10,inhu=False):
        data = Downloader.getContentFromUrl(url=link,data="",cookie="lang=english")
        html = ""
        if data.find("<script type='text/javascript'>eval(function(p,a,c,k,e")==-1:
            finalCookie = "lang=english"
            #build form
            if data.find('type="hidden" name="op" value="')>-1:
                op = Decoder.extract('type="hidden" name="op" value="','"',data)
                id = Decoder.extract('type="hidden" name="id" value="','"',data)
                fname = Decoder.extract('type="hidden" name="fname" value="','"',data)
                usr_login = Decoder.extract('type="hidden" name="usr_login" value="','"',data)
                referer = Decoder.extract('type="hidden" name="referer" value="','"',data)
                hash = Decoder.extract('type="hidden" name="hash" value="','"',data)
                if inhu==False:
                    imhuman = Decoder.extract('type="submit" name="imhuman" value="','"',data).replace("+"," ")
                    form = {
                        'op':op,
                        'id':id,
                        'usr_login':usr_login,
                        'fname':fname,
                        'referer':referer,
                        'hash':hash,
                        'imhuman':imhuman}
                else:
                    btn_download = ""
                    inhu = Decoder.extract('type="hidden" name="inhu" value="','"',data)
                    gfk = Decoder.extract("name: 'gfk', value: '","'",data)
                    vhash = Decoder.extract("name: '_vhash', value: '","'",data)
                    form = {
                        'op':op,
                        'id':id,
                        'usr_login':usr_login,
                        'fname':fname,
                        'referer':referer,
                        'hash':hash,
                        'inhu':inhu,
                        '_vhash':vhash,
                        'gfk':gfk,
                        'imhuman':btn_download}
                if op != '':
                    time.sleep(waitTime)
                    html = Decoder.getContent(link,form,link,finalCookie,False).read()
        else:
            html = data

        return html

    @staticmethod
    def removeHTML(body):
        finalText = ""
        while "<script" in body:
            replaceBy = Decoder.extractWithRegex("<script","</script>",body)
            body = body.replace(replaceBy,"")
        while "<" in body:
            index = body.find("<")
            targetLine = body[:index]
            finalText += targetLine.strip()
            body = body[body.find(">")+1:]
        body = body.strip()
        return finalText

    @staticmethod
    def decodeStreamable(link):
        html = Downloader.getContentFromUrl(link)
        flashContent = Decoder.extract('<object','</object',html)
        movie = ""
        flashVars = ""
        for content in flashContent.split('<param'):
            value = Decoder.extract('value="','"',content)
            name = Decoder.extract('name="','"',content)
            if name=="movie" or name=="player":
                movie = value
            elif name=="FlashVars":
                flashVars = value
        swfUrl = "http://www.streamable.ch"+movie
        flashVars = flashVars[flashVars.find("="):]
        decodedFlashvars = base64.standard_b64decode(flashVars)
        logger.debug("decoded url is: "+decodedFlashvars)
        response = Downloader.getContentFromUrl(decodedFlashvars)
        token = Decoder.extract("\"token1\":\"","\"",response)
        finalLink = base64.standard_b64decode(token)
        logger.debug("final link is: "+finalLink)
        return finalLink

    @staticmethod
    def decodeVidggTo(link):
        referer = "http://www.vidgg.to/player/cloudplayer.swf"
        html = Downloader.getContentFromUrl(link)
        file = Decoder.extract("flashvars.file=\"",'";',html)
        key = Decoder.extract("flashvars.filekey=\"",'";',html)
        url2 = "http://www.vidgg.to/api/player.api.php?pass=undefined&key="+key+"&user=undefined&numOfErrors=0&cid3=undefined&cid=1&file="+file+"&cid2=undefined"
        bruteResponse = Downloader.getContentFromUrl(url2)
        finalLink = Decoder.extract("url=","&title",bruteResponse)
        logger.debug("Final link is: "+finalLink)
        return finalLink

    @staticmethod
    def decodeBestreams(link):
        html = Decoder.getFinalHtmlFromLink(link) #has common attributes in form with powvideo and others
        file = Decoder.extract('streamer: "','"',html)
        playpath = "mp4:"+Decoder.extract("file: \"","\",",html)
        file += " playPath="+playpath+" swfUrl=http://bestreams.net/player/player.swf pageUrl="+link+" live=1 flashver=WIN/2019,0,0,226 timeout=14" #is an rtmp
        logger.debug("Final link is: "+file)
        return file

    @staticmethod
    def decodeLetwatch(link):
        html = Downloader.getContentFromUrl(link,"","","",False,True)
        try:
            encodedMp4File = Decoder.extract("<script type='text/javascript'>eval(function(p,a,c,k,e,d)","</script>",html)
        except:
            pass
        mp4File = jsunpack.unpack(encodedMp4File) #needs un-p,a,c,k,e,t|d
        mp4File = Decoder.extract('{file:"','",',mp4File)
        return mp4File

    @staticmethod
    def decodeVidag(link):
        html = Downloader.getContentFromUrl(link,"","","",False,True)
        try:
            encodedMp4File = Decoder.extract("<script type='text/javascript'>eval(function(p,a,c,k,e,d)","</script>",html)
        except:
            pass
        mp4File = jsunpack.unpack(encodedMp4File) #needs un-p,a,c,k,e,t|d
        mp4File = Decoder.extract(',{file:"','",',mp4File)
        return mp4File

    @staticmethod
    def decodeIdowatch(link):
        logger.debug("decoding idowatch link: "+link)
        html = Decoder.getContent(link,'').read()
        logger.debug(html)
        if html.find('file:"')>-1:
            file = Decoder.extract('file:"','",',html)
        else:
            file = Decoder.rExtractWithRegex('http:','.mp4',html)
        logger.debug("found file: "+file)
        return file+"|"+Downloader.getHeaders("http://idowatch.net/player6/jwplayer.flash.swf")

    @staticmethod
    def decodeIguide(iframeUrl3,iframeUrl2=''):
        logger.debug("iguide url is: "+iframeUrl3)
        html4 = Downloader.getContentFromUrl(iframeUrl3,"autoplay=true",Downloader.cookie,iframeUrl2)
        logger.debug("part 2 of iguide")
        #at this point is a similar logic than streamlive.to (probably because like always it's the same server), builds the link
        swfUrl = Decoder.rExtractWithRegex("http://",".swf",html4)
        logger.debug("using swfUrl: "+swfUrl)
        tokenUrl = Decoder.extractWithRegex("http://www.iguide.to/serverfile.php?id=",'"',html4)
        tokenUrl = tokenUrl[:(len(tokenUrl)-1)]
        token = Downloader.getContentFromUrl(tokenUrl,"",Downloader.cookie)
        logger.debug("obtained token from iguide: "+token)
        token = Decoder.extract('{"token":"','"}',token)
        file = Decoder.extract("'file': '","',",html4).replace('.flv','')
        streamer = Decoder.extract("'streamer': '","',",html4).replace("\\","")
        link = streamer+" playpath="+file+" live=1 token="+token+" swfUrl="+swfUrl+" pageUrl="+iframeUrl3
        logger.debug("built a link to be used: "+link)
        return link

    @staticmethod
    def decodeAAScript(script):
        '''
        see Aadecoder() from http://pastebin.com/cD0kT82B, which was the real first method
        TODO: implement original javascript decoder
        http://pastebin.com/CnMsw3xw
        these links are the reference for the following code
        http://pastebin.com/8HtaXMSg
        http://pastebin.com/PcMyxtPX
        '''
        #replace all figures, math, symbols and other offuscated
        script = script.replace("((ﾟｰﾟ) + (ﾟｰﾟ) + (ﾟΘﾟ))", "9")
        script = script.replace("((ﾟｰﾟ) + (ﾟｰﾟ))","8")
        script = script.replace("((ﾟｰﾟ) + (o^_^o))","7")
        script = script.replace("((o^_^o) +(o^_^o))","6")
        script = script.replace("((ﾟｰﾟ) + (ﾟΘﾟ))","5")
        script = script.replace("(ﾟｰﾟ)","4")
        script = script.replace("(o^_^o)","3")
        script = script.replace("((o^_^o) - (ﾟΘﾟ))","2")
        script = script.replace("(ﾟΘﾟ)","1")
        script = script.replace("(+!+[])","1")
        script = script.replace("(c^_^o)","0")
        script = script.replace("(0+0)","0")
        script = script.replace("(ﾟДﾟ)[ﾟεﾟ]","\\")
        script = script.replace("(3 +3 +0)","6")
        script = script.replace("(3 - 1 +0)","2")
        script = script.replace("(!+[]+!+[])","2")
        script = script.replace("(-~-~2)","4")
        script = script.replace("(-~-~1)","3")
        decodestring = re.search(r"\\\+([^(]+)", script, re.DOTALL | re.IGNORECASE).group(1)
        decodestring = "\\+"+ decodestring
        decodestring = decodestring.replace("+","")
        decodestring = decodestring.replace(" ","")
        for octc in (c for c in re.findall(r'\\(\d{2,3})', decodestring)):
            decodestring = decodestring.replace(r'\%s' % octc, chr(int(octc, 8)))
        decodestring = decodestring.replace("\\/","/")
        url = re.search(r"vr\s?=\s?\"|'([^\"']+)", decodestring, re.DOTALL | re.IGNORECASE).group(1)
        return url

    @staticmethod
    def decodeOpenload(link): #decode javascript link like Firefox
        mediaId = Decoder.extract("/f/","/",link)
        logger.debug("mediaId is: "+mediaId)
        link = link.replace('/f/', '/embed/')
        html = Downloader.getContentFromUrl(link,"data=data","","",False,True) #make post, with get there is an infinite loop
        #extract script
        script = re.search(r"<video(?:.|\s)*?<script\s[^>]*?>((?:.|\s)*?)</script", html, re.DOTALL | re.IGNORECASE).group(1)
        url = Decoder.decodeAAScript(script)
        logger.debug("decoded url is: "+url)
        return url


    @staticmethod
    def decodeOpenloadUsingOfficialApi(link): #API sucks, today it always returns a 509 with all logins xDDD
        #get cookies
        mediaId = Decoder.extract("/f/","/",link)
        embedUrl = 'https://openload.io/embed/'+mediaId
        headers = {}
        headers["Accept"] = "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        headers["Accept-Encoding"] = "gzip, deflate, br"
        headers["Accept-Language"] = "en-US,en;q=0.8,es-ES;q=0.5,es;q=0.3"
        headers["Connection"] = "keep-alive"
        headers["DNT"] = "1"
        headers["Host"] = "openload.co"
        headers["User-Agent"] = Downloader.USER_AGENT
        html = ""
        try:
            html = Downloader.getContentFromUrl(embedUrl,data="",cookie="",headers=headers,launchLocation=True,ajax=False)
        except:
            logger.debug("trying with the old method, before it was working fine so...")
            html = Decoder.getContent2(embedUrl)
            pass
        logger.debug("html is: "+html)
        logger.debug("using cookie 1: "+Downloader.cookie)
        logger.debug("Media id for openload is: "+mediaId)
        key = "oaA-MbZo"
        login = "f750b26513f64034"
        extra = "&login="+login+"&key="+key #this avoid captcha petition
        link2 = "https://api.openload.io/1/file/dlticket?file="+mediaId+extra
        data = Downloader.getContentFromUrl(link2,"",Downloader.cookie,embedUrl,True,False)
        logger.debug("jsonData: "+data)
        js_result = json.loads(data)
        logger.debug("sleeping... "+str(js_result['result']['wait_time']))
        time.sleep(int(js_result['result']['wait_time']))
        link3 = 'https://api.openload.io/1/file/dl?file=%s&ticket=%s' % (mediaId, js_result['result']['ticket'])
        logger.debug("using cookie 2: "+Downloader.cookie)
        result = Downloader.getContentFromUrl(link3,"",Downloader.cookie,embedUrl,True,False)
        logger.debug("jsonData 2: "+result)
        js_result2 = json.loads(result)
        file = js_result2['result']['url'] + '?mime=true'
        logger.debug("Built final link: "+file)
        return file

    @staticmethod
    def decodePrivatestream(html,referer):
        rtmpUrl = "rtmp://31.220.40.63/privatestream/"
        logger.debug("trying to get playpath from html...")
        if html.find("var v_part = '")>-1:
            logger.debug("detected playpath...")
            playPath = Decoder.extract("var v_part = '","';",html)[len("/privatestream/"):]
            swfUrl = "http://privatestream.tv/js/jwplayer.flash.swf"
            rtmpUrl = rtmpUrl+playPath+" playPath="+playPath+" swfUrl="+swfUrl+" live=1 timeout=12 pageUrl="+referer
            logger.debug("final link:"+rtmpUrl)
        else:
            logger.info("nothing detected, returning incomplete link :(")
        return rtmpUrl

    @staticmethod
    def decodeMipsplayer(html,referer):
        newParam = Decoder.extractParams(html)
        finalUrl = "rtmp://46.165.220.232/live playPath="+newParam+" swfVfy=1 timeout=15 live=true conn=S:OK swfUrl=http://www.mipsplayer.com/content/scripts/fplayer.swf flashver=WIN/2019,0,0,226 ccommand=false pageUrl="+referer
        return finalUrl

    @staticmethod
    def extractParams(html):
        param = Decoder.extract("so.addParam('FlashVars', '","');",html) #brute params, needs a sort
        logger.debug("brute params are: "+param)
        firstArgument = Decoder.extract('s=','&',param)
        id = Decoder.extract('id=','&',param)
        pk = param[param.find('pk=')+len('pk='):]
        newParam = firstArgument+"?id="+id+"&pk="+pk #format param
        logger.debug("param is now: "+newParam)
        return newParam

    @staticmethod
    def decodeLiveFlash(html,referer):
        newParam = Decoder.extractParams(html)
        finalUrl = "rtmp://46.165.196.40/stream playPath="+newParam+" swfVfy=1 timeout=10 conn=S:OK live=true swfUrl=http://www.liveflashplayer.net/resources/scripts/fplayer.swf flashver=WIN/2019,0,0,226 pageUrl="+referer
        return finalUrl

    @staticmethod
    def decodeUcaster(html,referer):
        newParam = Decoder.extractParams(html)
        finalUrl = "rtmp://178.162.199.155/live/ playPath="+newParam+" swfVfy=1 timeout=10 conn=S:OK live=true swfUrl=http://www.embeducaster.com/static/scripts/fplayer.swf flashver=WIN/2019,0,0,226 pageUrl="+referer
        return finalUrl

    @staticmethod
    def decode247bay(html,referer):
        newParam = Decoder.extractParams(html)
        finalUrl = "rtmp://94.102.51.67/stream playPath="+newParam+" swfVfy=1 timeout=10 conn=S:OK live=true swfUrl=http://www.247bay.tv/static/scripts/eplayer.swf flashver=WIN/2019,0,0,226 pageUrl="+referer
        return finalUrl

    @staticmethod
    def extractSawlive(scriptSrc,iframeUrl):
        encryptedHtml = Downloader.getContentFromUrl(scriptSrc,"","",iframeUrl)
        decryptedUrl = Decoder.decodeSawliveUrl(encryptedHtml)
        html3 = Downloader.getContentFromUrl(decryptedUrl,"",Downloader.cookie,iframeUrl) #fix, it must use the same referer
        logger.debug("decrypted sawlive url content obtained!")
        logger.debug("final html is: "+html3)
        #ok, now extract flash script content
        flashContent = Decoder.extract("var so = new SWFObject('","</script>",html3)
        file = Decoder.extract("'file', ",");",flashContent)
        logger.debug("proccessing brute file: "+file)
        #now proccess file, it can be a figure so needs to be appended if contains +
        if file.find("+")>1:
            newFile = ""
            for target in file.split("+"):
                seekedString = "var "+target+" = '"
                if html3.find(seekedString)>-1:
                    value = Decoder.extract(seekedString,"'",html3)
                    newFile += value
                else:
                    newFile += target
                logger.debug("now file is: "+newFile)
            file = newFile
            logger.debug("updated file to: "+file)
        else:
            file = file.replace("'","") #clean
        rtmpUrl = ""
        if flashContent.find("'streamer', '")>.1:
            rtmpUrl = Decoder.extract("'streamer', '","');",flashContent)
        else:
            rtmpVar = Decoder.extract("'streamer', ",");",flashContent)
            seekedString = "var "+rtmpVar+" = '"
            rtmpUrl = Decoder.extract(seekedString,"';",html3)
        swfUrl = "http://static3.sawlive.tv/player.swf" #default
        #update swf url
        swfUrl = flashContent[:flashContent.find("'")]
        logger.debug("updated swf player to: "+swfUrl)
        if rtmpUrl=='' and file.find("http://")>-1 and file.find(".jpg")==-1:
            finalRtmpUrl = file #it's a redirect with an .m3u8, so it's used
        else:
            if 'function' in rtmpUrl:
                content2 = Downloader.getContentFromUrl(file,"","",swfUrl)
                logger.debug(content2)
                finalRtmpUrl = file+"|"+Downloader.getHeaders(swfUrl)
            else:
                finalRtmpUrl = rtmpUrl+" playpath="+file+" swfUrl="+swfUrl+" live=1 conn=S:OK pageUrl="+decryptedUrl+" timeout=12"
        return finalRtmpUrl

    @staticmethod
    def decodeSawliveUrl(encryptedHtml):
        vars = {}
        finalUrl = ""
        logger.debug("encrypted iframe is: "+encryptedHtml)
        if "eval(function(p,a,c,k,e" in encryptedHtml:
            try:
                encryptedHtml = jsunpack.unpack(encryptedHtml)
            except:
                logger.debug("Something goes wrong, trying unpack with old library")
                try:
                    encryptedHtml = jsunpackOld.unpack(encryptedHtml)
                except:
                    logger.error("Could not unpack content")
                    pass
            encryptedHtml = encryptedHtml.replace("\\'","'")
            logger.debug("now encrypted iframe content is: "+encryptedHtml)
        elif ",a,c,k,e" in encryptedHtml:
            logger.debug("changed packer/d. replacing with new")
            a = Decoder.rExtract("function(",",a,c,k,e,",encryptedHtml)
            r = Decoder.extract(",a,c,k,e,",")",encryptedHtml)
            logger.debug("brute a is: "+a)
            logger.debug("brute r is: " + r)
            encryptedHtml = encryptedHtml.replace(a,"a")
            encryptedHtml = encryptedHtml.replace(r, "r")
            finalUrl = 'http://www3.sawlive.tv/embed/watch/'+Decoder.extract('|11|',"|",encryptedHtml)+"/"+Decoder.extract('|10|',"|",encryptedHtml)
            logger.debug("new brute url is: "+finalUrl)

        varPart = ""
        if ";document.write" in encryptedHtml:
            #first extract var values and append it to an array
            varPart = encryptedHtml[0:encryptedHtml.find(';document.write')]

        if len(varPart)>0:
            logger.debug("launching varPart logic...")
            for varElement in varPart.split(';'): #loop each var
                logger.debug("checking javascript assign: "+varElement)
                if varElement.find('=')>-1:
                    bruteElement = varElement.split('=')
                    logger.debug("Brute element is at this time: "+bruteElement[1])
                    if "'" in bruteElement[1]:
                        logger.debug("checking content: "+bruteElement[1])
                        if "+'/'+" not in bruteElement[1]:
                            extractedElement = Decoder.executeExtractedElement(bruteElement[1],varPart)
                            bruteElement[0] = bruteElement[0].replace("var ", "")
                            vars[bruteElement[0]] = extractedElement
                        else:
                            bruteElements = bruteElement[1].split("+'/'+")
                            extractedContent = ""
                            for bruteElementSplit in bruteElements:
                                logger.debug("using for this part brute element splited by: "+bruteElementSplit)
                                first = (len(extractedContent)==0)
                                extractedContent += vars[bruteElementSplit]  # Decoder.executeExtractedElement(target, varPart)
                                if first:
                                    logger.debug("detected first time... appending / character (needed)")
                                    extractedContent += "/"

                                logger.debug("at this moment extracted content is: "+extractedContent)

                            logger.debug("done! now saving logic...")
                            bruteElement[0] = bruteElement[0].replace("var ", "")
                            logger.debug("extracted value is: " + extractedContent + ", assigning it to " + bruteElement[0])
                            vars[bruteElement[0]] = extractedContent
                    else:
                        logger.debug("Not found ' character in value "+bruteElement[1]+". Probably it's an append. ("+bruteElement[0]+")")
                        if '+' in bruteElement[1]:
                            bruteElements = bruteElement[1].split("+")
                            extractedContent = ""
                            for target in bruteElements:
                                logger.debug("proccessing... "+target)
                                extractedContent += vars[target] #Decoder.executeExtractedElement(target, varPart)
                            bruteElement[0] = bruteElement[0].replace("var ", "")
                            logger.debug("extracted value is: " + extractedContent + ", assigning it to " + bruteElement[0])
                            vars[bruteElement[0]] = extractedContent
            #second extract src part for a diagnostic
            if encryptedHtml.find(' src="')>-1:
                bruteSrc = Decoder.extract(' src="','"></iframe>',encryptedHtml)
            elif encryptedHtml.find(" src=\"")>-1:
                bruteSrc = Decoder.extract(' src="','"></iframe>',encryptedHtml)
            logger.debug("bruteSrc is: "+bruteSrc)
            finalUrl = ""
            if bruteSrc.find("+")>-1:
                for bruteUrlPart in bruteSrc.split("+"):
                    if bruteUrlPart.find("unescape")>-1:
                        extractedValue = Decoder.extract("(",")",bruteUrlPart)
                        if extractedValue.find("'")>-1: #it means encoded html
                            extractedValue = Decoder.extract("'","'",extractedValue)
                            logger.debug("trace 1 for brutesrc")
                            finalUrl += urllib.unquote(extractedValue)
                        else: #it means a var, seek it
                            if vars.has_key(extractedValue):
                                finalUrl += vars[extractedValue]
                        logger.debug("trace 2 for brutesrc")
                    else:
                        if bruteUrlPart.find("'")==0:#there is a var
                            if vars.has_key(bruteUrlPart):
                                finalUrl += vars[bruteUrlPart]
                                logger.debug("trace 3 for brutesrc")
                            else:
                                bruteUrlPart = bruteUrlPart.replace("'","")
                                finalUrl+=bruteUrlPart
                                logger.debug("trace 4 for brutesrc")
                        else: #brute text, paste it without the final "'" if it contains that character
                            bruteUrlPart = bruteUrlPart.replace("'","")
                            logger.debug("len of "+bruteUrlPart+" part is: "+str(len(bruteUrlPart)))
                            if vars.has_key(bruteUrlPart):
                                logger.debug("trace 5 for brutesrc: "+bruteUrlPart+","+vars[bruteUrlPart])
                                if vars[bruteUrlPart].find('"')==-1:
                                    finalUrl += vars[bruteUrlPart]
                                else:
                                    for bruteUrlPart2 in vars[bruteUrlPart].split("+"):
                                        logger.debug("seek key: "+bruteUrlPart2)
                                        if vars.has_key(bruteUrlPart2):
                                            #get value
                                            valueVar = vars[bruteUrlPart2]
                                            if '.replace(' in valueVar:
                                                #jzje=jzje.replace(ejzj,"MTRmYW");
                                                logger.debug("replacing second value un vars... "+valueVar)
                                                valueVar = Decoder.extract(",",");",valueVar)
                                                vars[bruteUrlPart2] = valueVar
                                                logger.debug("replaced! " + valueVar)
                                        if vars.has_key(bruteUrlPart2) and bruteUrlPart2.find('"')==-1:
                                            finalUrl += vars[bruteUrlPart2].replace('"',"")
                                        elif len(bruteUrlPart.strip())>2:
                                            logger.debug("brute url part: "+bruteUrlPart)
                                            finalUrl+=bruteUrlPart
                                            logger.debug("brute text included2: "+bruteUrlPart)
                            else:
                                for key in vars:
                                    logger.debug("discarted: "+key)
                                logger.debug("It's not waste, text is: "+bruteUrlPart)
                                finalUrl+=bruteUrlPart
                    logger.debug("now finalUrl is: "+urllib.unquote(finalUrl))
            finalUrl = urllib.unquote(finalUrl) #finally translate to good url
            if finalUrl.find("unezcapez(")>-1:
                logger.debug("replacing url new encoding...")
                finalUrl = finalUrl.replace("unezcapez(","").replace(')','') #little fix for new coding, it will be included in the previews revision
            logger.info("Decrypted url is: "+finalUrl)
        elif len(finalUrl)==0:
            #use alternative logic with encrypted iframe
            logger.debug('Using alternative algorithm...')
            if 'else{return' in encryptedHtml:
                partialUrl = Decoder.extract(' src="','+\'">',encryptedHtml)
                logger.debug("brute url with logic call is: "+partialUrl)
                finalUrl = ""
                for urlPart in partialUrl.split("+"):
                    if "('" in urlPart:
                        partialURI = ""
                        target = Decoder.extract("('","')",urlPart)
                        logger.debug("target is: "+target)
                        if '"'+target+'"){return"' in encryptedHtml:
                            partialURI = Decoder.extract('"'+target+'"){return"','"',encryptedHtml)
                        else:
                            partialURI = Decoder.extract('else{return"','"',encryptedHtml)
                        logger.debug("partialURI is: "+partialURI)
                        if len(partialURI)>0:
                            finalUrl += partialURI
                    else:
                        finalUrl += urlPart.replace("'","")
            else:
                logger.debug("else logic for alternative algorithm...")
                second = Decoder.rExtract('"','";return',encryptedHtml)
                first = Decoder.rExtract(',"','")+',encryptedHtml)
                if len(first)<34:
                    split = Decoder.extract('watch|','.split',encryptedHtml)
                    logger.debug("brute split is: "+split)
                    for splitted in split.split("|"):
                        if len(splitted)==34:
                            logger.debug("patching first arg with: "+splitted)
                            first = splitted
                else:
                    logger.debug("first is right: "+first+", length: "+str(len(first)))
                finalUrl = "http://www3.sawlive.tv/embed/watch/"+first+"/"+second
        return finalUrl

    @staticmethod
    def executeExtractedElement(value,varPart):
        extractedElement = Decoder.extract("'", "'", value)
        if extractedElement.find("+") > -1:
            for currentVarSubElement in extractedElement.split("+"):
                if len(currentVarSubElement) > 0 and '"' not in currentVarSubElement:
                    logger.debug("IF: " + currentVarSubElement)
                    logger.debug("using var: " + currentVarSubElement)
                    preSubFix = "var " + currentVarSubElement + "=";
                    valueInternalVar = varPart[varPart.find(preSubFix) + len(preSubFix) + 1:]
                    logger.debug("Internal var provisional is: " + valueInternalVar)
                    valueInternalVar = valueInternalVar[:valueInternalVar.find("'")]  # TODO, change splitter char
                    logger.debug("Internal var final is: " + valueInternalVar)
        return extractedElement

    @staticmethod
    def decodeLetonTv(html,referer):
        rtmpUrl = "rtmp://31.200.0.186"
        logger.debug("trying to get playpath from html...")
        if html.find("var v_part = '")>-1:
            logger.debug("detected playpath...")
            playPath = Decoder.extract("var v_part = '","';",html)
            swfUrl = "http://files.leton.tv/jwplayer.flash.swf"
            rtmpUrl = rtmpUrl+playPath+" playPath="+playPath+" swfUrl="+swfUrl+" live=1 timeout=12 pageUrl="+referer
        else:
            logger.info("nothing detected, returning incomplete link :(")
        return rtmpUrl

    @staticmethod
    def decodeBussinessApp(html,iframeReferer):
        response = ""
        token = ""
        doIt = False
        jsFile = "http://www.sunhd.info/jwplayer6/jwplayer.js"
        if html.find("jwplayer5/addplayer/jwplayer.js")>-1:
            jsFile = Decoder.rExtractWithRegex("http://","jwplayer5/addplayer/jwplayer.js",html)
            logger.debug("updated js player to: "+jsFile)
        elif html.find("http://www.playerhd1.pw")>-1:
            jsFile = "http://www.playerhd1.pw/jwplayer5/addplayer/jwplayer.js"
        try:
            token = Decoder.extractBusinessappToken(iframeReferer,jsFile)
        except:
            logger.error("Error, trying without token")
            pass

        swfUrl = "http://www.sunhd.info/jwplayer6/jwplayer.flash.swf"
        if html.find("jwplayer5/addplayer/jwplayer.flash.swf")>-1: #http://www.playerapp1.pw/jwplayer5/addplayer/jwplayer.flash.swf
            swfUrl = Decoder.rExtractWithRegex("http://","jwplayer5/addplayer/jwplayer.flash.swf",html)
            logger.debug("updated swf player to: "+swfUrl)
        elif jsFile.find("businessapp1.pw")==-1:
            swfUrl = "http://"+Decoder.extract('//',"/",jsFile)+"/jwplayer5/addplayer/jwplayer.flash.swf"
            logger.debug("updated swf player to: "+swfUrl)
        elif html.find("http://www.playerhd1.pw")>-1:
            swfUrl = "http://www.playerhd1.pw/jwplayer5/addplayer/jwplayer.flash.swf"

        if html.find('<input type="hidden" id="ssx1" value="')>-1:
            ssx1 = Decoder.extract('<input type="hidden" id="ssx1" value="','"',html)
            ssx4 = Decoder.extract('<input type="hidden" id="ssx4" value="','"',html)
            escaped = Decoder.extract("<script type='text/javascript'>document.write(unescape('","'",html)
            unescaped = urllib.unquote(escaped)
            decodedssx1 = base64.standard_b64decode(ssx1)
            decodedssx4 = base64.standard_b64decode(ssx4)
            iframeReferer = urllib.unquote_plus(iframeReferer.replace("+","@#@")).replace("@#@","+") #unquote_plus replaces '+' characters
            if decodedssx4.find(".m3u8")>-1:
                logger.debug("Found simple link: "+decodedssx4)
                if iframeReferer.find("ponlatv.com")>-1:
                    iframeReferer = "http://www.ponlatv.com/jwplayer6/jwplayer.flash.swf"
                logger.debug("using referer url: "+iframeReferer)
                host = decodedssx4[decodedssx4.find("://")+len("://"):]
                subUrl = ""
                logger.info("url is: "+host)
                if host.find("/")>-1:
                    host = host[0:host.find("/")]
                headers = {
                    "User-Agent": Downloader.USER_AGENT,
                    "Accept-Language" : "en-US,en;q=0.8,es-ES;q=0.5,es;q=0.3",
                    "Accept-Encoding" : "gzip, deflate",
                    "Referer" : iframeReferer,
                    "Host":host,
                    "DNT":"1",
                    "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                }
                response = Downloader.getContentFromUrl(url=decodedssx4,referer=iframeReferer,headers=headers)
                logger.debug("html is: "+response)
                if response.find("chunklist.m3u8")>-1:
                    finalSimpleLink2 = decodedssx4[:decodedssx4.rfind("/")+1]+"chunklist.m3u8"
                    response = Decoder.getContent(finalSimpleLink2,"",iframeReferer).read()
                    logger.debug("response for m3u8(1): "+response)
                    response = finalSimpleLink2+"|Referer="+iframeReferer
                else:
                    logger.debug("response for m3u8(2): "+response)
                    response = decodedssx4
            elif token!= "" and decodedssx4.find("vod/?token=")>-1:
                app = decodedssx4[decodedssx4.find("vod/?token="):]
                response = decodedssx4+" playpath="+decodedssx1+" app="+app+" swfUrl="+swfUrl+" token="+token+" flashver=WIN/2019,0,0,226 live=true timeout=14 pageUrl="+iframeReferer
            elif token!="":
                app = decodedssx4[decodedssx4.find("redirect/?token="):]
                response = decodedssx4+" playpath="+decodedssx1+" app="+app+" swfUrl="+swfUrl+" token="+token+" flashver=WIN/2019,0,0,226 live=true timeout=14 pageUrl="+iframeReferer
            else:#m3u8 file
                logger.debug("link1: "+decodedssx1)
                logger.debug("link2: "+decodedssx4)
            logger.debug("to player: "+response)
        else:
            playPath = ""
            rtmpValue = ""
            hasPatch = str(XBMCUtils.getSettingFromContext(int(sys.argv[1]), "localproxy_patch"))
            logger.debug("has patch = "+hasPatch)
            enabled = bool(hasPatch == "true")
            #i = 0
            finalSimpleLink = ""
            logger.debug("html is: "+html)
            oldHtml = html
            if html.find('<input type="hidden" id="')>-1:
                for splittedHtml in html.split('<input type="hidden" id="'):
                    if splittedHtml.find("DOCTYPE html PUBLIC")==-1 and splittedHtml.find(' value=""')==-1:
                        logger.debug("processing hidden: "+splittedHtml)
                        extracted = splittedHtml[splittedHtml.find('value="')+len('value="'):]
                        extracted = extracted[0:extracted.find('"')]
                        logger.debug("extracted hidden value: "+extracted)
                        if playPath == "":
                            playPath = base64.standard_b64decode(extracted)
                        else:
                            rtmpValue = base64.standard_b64decode(extracted)
                        decodedAndExtracted = base64.standard_b64decode(extracted)
                        logger.info("original: "+extracted+", extracted: "+decodedAndExtracted)
                        if decodedAndExtracted.find(".m3u8")>-1:
                            finalSimpleLink = decodedAndExtracted
                        else:
                            logger.debug("not used: "+decodedAndExtracted)
                            #TODO extracted
                            if '/' in extracted:
                                #new way, use API
                                doIt = True
                                html = Decoder.extract("<script type='text/javascript'>","</script>",html)
                                logger.debug("new html is: "+html)
                                html = urllib.unquote(html)
                                logger.debug("parsed html is: " + html)
                    #i+=1
            else:
                doIt = True
            if doIt:
                #ok, lets do it
                targetVar = Decoder.extract("v_cod1: ",",",html)
                targetVar2 = Decoder.extract("v_cod2: ", ",", html)
                if " " in targetVar:
                    targetVar = targetVar[:targetVar.find(" ")]
                if " " in targetVar2:
                    targetVar2 = targetVar2[:targetVar2.find(" ")]
                cod1 = ''
                v_cod1 = ''
                cod2 = ''
                v_cod2 = ''
                logger.debug("v_cod1 --> "+targetVar)
                if 'var '+targetVar+' = "document.getElementById(\'' in html:
                    targetValue = Decoder.extract('var '+targetVar+' = "document.getElementById(\'','\'',html)
                    logger.debug("logged var at this time is: "+targetValue)
                elif targetVar+' = document.getElementById(\'' in oldHtml:
                    targetValue = Decoder.extract(targetVar+' = document.getElementById(\'','\'',oldHtml)
                    logger.debug("logged GLOBAL VAR at this time is: "+targetValue)
                    targetValue = Decoder.extract('<input type="hidden" id="'+targetValue+'" value="','"',oldHtml)
                    logger.debug("NOW logged GLOBAL VAR 1 value is: " + targetValue)
                    cod1 = targetValue
                    v_cod1 = cod1
                elif 'var '+targetVar+' = "' in html:
                    targetValue = Decoder.extract('var ' + targetVar + ' = "', '"', html)
                    logger.debug("logged var at this time is (2): "+targetValue)
                else:
                    logger.debug("discarted 1 hidden: \""+targetVar+' = document.getElementById(\'')
                    logger.debug("wasted html is: "+html)
                    targetValue = Decoder.extract('var '+targetVar+' = "','"',html)
                    logger.debug("based64 var is: " + targetValue)

                logger.debug("v_cod2 --> " + targetVar2)
                if 'var ' + targetVar2 + ' = "document.getElementById(\'' in html:
                    targetValue2 = Decoder.extract('var ' + targetVar2 + ' = "document.getElementById(\'', '\'', html)
                    logger.debug("logged var at this time is: " + targetValue2)
                elif targetVar2 + ' = document.getElementById(\'' in oldHtml:
                    targetValue2 = Decoder.extract(targetVar2 + ' = document.getElementById(\'', '\'', oldHtml)
                    logger.debug("logged GLOBAL VAR at this time is: " + targetValue)
                    targetValue2 = Decoder.extract('<input type="hidden" id="' + targetValue2 + '" value="', '"', oldHtml)
                    logger.debug("NOW logged GLOBAL VAR 2 value2 is: " + targetValue2)
                    cod2 = targetValue2
                    v_cod2 = cod2
                elif 'var ' + targetVar2 + ' = "' in html:
                    targetValue2 = Decoder.extract('var ' + targetVar2 + ' = "', '"', html)
                    logger.debug("logged var at this time is (2): " + targetValue2)
                else:
                    logger.debug("discarted 2 hidden: \"" + targetVar2 + ' = document.getElementById(\'')
                    logger.debug("wasted html is: " + html)
                    targetValue2 = Decoder.extract('var ' + targetVar2 + ' = "', '"', html)
                    logger.debug("based64 var is: " + targetValue2)
                #tokenPage = base64.decodestring(targetValue)
                tokenPage = 'sc_tk.php'
                logger.debug("tokenPage is: " + tokenPage)
                if "http" not in tokenPage:
                    host = iframeReferer[iframeReferer.find("://") + 3:]
                    host = host[:host.find("/")]
                    tokenPage = "http://"+host+"/"+tokenPage
                #now get vars v_cod1 and v_cod2
                if cod1 == '':
                    cod1 = Decoder.extract('v_cod1: ',',',html)
                if cod2 == '':
                    cod2 = Decoder.extract('v_cod2: ', '}', html).strip()
                if v_cod1 == '':
                    v_cod1 = Decoder.extract('var ' + cod1 + ' = "', '"', html)
                if v_cod2 == '':
                    v_cod2 = Decoder.extract('var ' + cod2 + ' = "', '"', html)
                logger.debug("USING FINAL V_CODS --> v_cod1: "+v_cod1+", v_cod2: "+v_cod2)
                #form = {'v_cod1':v_cod1,'v_cod2':v_cod2}
                #formUrl = urllib.urlencode(form)
                rand13 = Decoder.getTimestamp()
                logger.debug("rand: "+rand13)
                #rand13="145"+str(random.random())[2:12]
                rand16 = '170' + str(random.random())[2:15]
                rand13_2 = Decoder.getTimestamp()#"145" + str(random.random())[2:12]
                tokenPage2=tokenPage+"?_="+rand13_2+"&callback=jQuery"+rand16+"_"+rand13#+"&v_cod1="+v_cod1+"&v_cod2="+v_cod2
                tokens = urllib.urlencode({"v_cod1":v_cod1,"v_cod2":v_cod2})
                logger.debug("using first pseudourl: "+tokenPage2)
                logger.debug("using tokens: " + tokens)
                ajaxResponse = Downloader.getContentFromUrl(url=tokenPage2+"&"+tokens,data='',cookie='',referer=iframeReferer,ajax=True)
                logger.debug("response is: "+ajaxResponse)
                referer = ''
                if "file: '" in ajaxResponse:
                    finalSimpleLink = Decoder.extract("file: '","',",ajaxResponse).replace("\\","")
                    logger.debug("extracted with new way: "+finalSimpleLink)
                else:
                    jsonString = ajaxResponse[ajaxResponse.find("{"):ajaxResponse.find(")")]
                    logger.debug(jsonString)
                    jsonResponse = json.loads(jsonString)
                    referer = str(jsonResponse["result1"])
                    if "http" not in referer:
                        referer = "http://"+referer
                    finalSimpleLink = response = str(jsonResponse["result2"])
                    if "http" not in finalSimpleLink:
                        logger.debug('incomplete url, it\'s relative, so needs to be completed!')
                        finalSimpleLink = "http://www.dinostream.pw/jwplayer6.5/local2/"+finalSimpleLink
                        logger.debug("new final simple link is: "+finalSimpleLink)
                logger.debug("proxy server is: "+str(enabled))
                if enabled:
                    response = "http://127.0.0.1:46720?original-request=" + finalSimpleLink+"&referer="+referer
                    Decoder.launchLocalHttpProxy()
                else:
                    response = finalSimpleLink+"|"+Downloader.getHeaders(referer)
                logger.debug(response)
            if finalSimpleLink!="":
                logger.debug("Found simple link: "+finalSimpleLink)
                if iframeReferer.find("ponlatv.com")>-1 or finalSimpleLink.find("http://cdn.sstream.pw/live/")>-1:
                    iframeReferer = "http://www.ponlatv.com/jwplayer6/jwplayer.flash.swf"
                    logger.debug("setting is: "+str(enabled)+", for: "+str(finalSimpleLink))
                    response = finalSimpleLink
                    if enabled:
                        Decoder.launchLocalHttpProxy()
                        response = "http://127.0.0.1:46720?original-request="+finalSimpleLink.replace("/playlist.m3u8","/chunklist.m3u8")
                    else:
                        response = str(finalSimpleLink)+"|"+Downloader.getHeaders(iframeReferer)
                else:
                    logger.debug("using referer url: "+iframeReferer)
                    host = finalSimpleLink[finalSimpleLink.find("://")+len("://"):]
                    subUrl = ""
                    logger.info("url is: "+host)
                    if host.find("/")>-1:
                        host = host[0:host.find("/")]
                    headers = {
                        "User-Agent": Downloader.USER_AGENT,
                        "Accept-Language" : "en-US,en;q=0.8,es-ES;q=0.5,es;q=0.3",
                        "Accept-Encoding" : "gzip, deflate",
                        "Referer" : iframeReferer,
                        "Host":host,
                        "DNT":"1",
                        "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
                    }
                    response = Downloader.getContentFromUrl(url=finalSimpleLink,referer=iframeReferer,headers=headers)
                    if response.find("chunklist.m3u8")>-1:
                        finalSimpleLink2 = finalSimpleLink[:finalSimpleLink.rfind("/")+1]+response[response.find("chunklist.m3u8"):].strip()
                        #response = Decoder.getContent(finalSimpleLink2,"",iframeReferer,"").read()
                        #logger.debug("response for m3u8(a): "+response)
                        #extract an internal link to use, m3u8 list doesn't work anymore
                        logger.debug("appending headers to link...")
                        if enabled:
                            Decoder.launchLocalHttpProxy()
                            response = "http://127.0.0.1:46720?original-request="+finalSimpleLink2
                        else:
                            response = finalSimpleLink2+"|"+Downloader.getHeaders(iframeReferer)
                    else:
                        logger.debug("response for m3u8(b): "+response)
                        if enabled:
                            Decoder.launchLocalHttpProxy()
                            response = "http://127.0.0.1:46720?original-request="+finalSimpleLink
                        else:
                            response = finalSimpleLink+"|"+Downloader.getHeaders(iframeReferer)
            elif rtmpValue.find("vod/?token=")>-1:
                app = rtmpValue[rtmpValue.find("vod/?token="):]
                iframeReferer = urllib.unquote_plus(iframeReferer.replace("+","@#@")).replace("@#@","+") #unquote_plus replaces '+' characters
                token = Decoder.extractBusinessappToken(iframeReferer,jsFile)
                response = rtmpValue+" playpath="+playPath+" app="+app+" swfUrl="+swfUrl+" token="+token+" flashver=WIN/2019,0,0,226 live=true timeout=14 pageUrl="+iframeReferer
            elif rtmpValue.find("?token=play@")>-1:
                app = "redirect"+rtmpValue[rtmpValue.find("?token=play@"):]
                token = Decoder.extractBusinessappToken(iframeReferer,jsFile)
                response = rtmpValue+" playpath="+playPath+" app="+app+" swfUrl="+swfUrl+" token="+token+" flashver=WIN/2019,0,0,226 live=true timeout=14 pageUrl="+iframeReferer
        return response

    @staticmethod
    def getTimestamp():
        timestamp = str(time.time()).replace('.', '') + '0'
        if len(timestamp) == 12:
            timestamp = timestamp + '0'
        return timestamp

    @staticmethod
    def launchLocalHttpProxy():
        import os
        httpproxypath = XBMCUtils.getAddonInfo('path')
        serverPath = os.path.join(httpproxypath, 'proxy2.py')
        try:
            import requests
            requests.get('http://127.0.0.1:46720?original-request=http://mobile.harddevelop.com/index2.html')
            proxyIsRunning = True
        except:
            proxyIsRunning = False
        if not proxyIsRunning:
            XBMCUtils.executeScript(serverPath)

    @staticmethod
    def extractBusinessappToken(iframeReferer,jsUrl="http://www.businessapp1.pw/jwplayer5/addplayer/jwplayer.js"):
        token = "@@stop-stole@@" #some pages changes this token, so it depends on
        javascriptContent = Decoder.getContent(jsUrl,"",iframeReferer).read()
        extracted = Decoder.rExtract('["','"];',javascriptContent)
        token = extracted.replace("\\x","").decode("hex")
        logger.info("Extracted token: "+token)
        return token

    @staticmethod
    def decodeStreame(link):
        html = Decoder.getFinalHtmlFromLink(link) #has common attributes in form with powvideo and others
        return Decoder.extract('[{file:"','"',html)

    @staticmethod
    def decodeVidXtreme(link):
        return Decoder.decodePowvideo(link)

    @staticmethod
    def decodeStreamplay(link):
        return Decoder.decodePowvideo(link)

    @staticmethod
    def decodeThevideo(link):
        html = Decoder.getFinalHtmlFromLink(link,5,True)
        mp4Link = Decoder.rExtract(", file: '","'",html) #there are more qualities, so I get the last one which is the best of
        mp4Link = mp4Link[0:mp4Link.find("'")]
        logger.info("found link: "+mp4Link)
        return mp4Link

    @staticmethod
    def decodeStreamin(link):
        ''' This method is not working anymore, but link is provided, so the code is kept
        html = Decoder.getFinalHtmlFromLink(link,5)
        mp4File = Decoder.extract("config:{file:'","'",html)
        logger.info('found link: '+mp4File)
        return mp4File
        '''
        html = Decoder.getFinalHtmlFromLink(link, 5)
        file = Decoder.extract('file: "','"', html)
        rtmp = Decoder.extract('streamer: "','"', html)
        swfPlayer = Decoder.extract('type: "flash", src: "','"', html)
        key = file[file.find('?h='):]
        playPath = "mp4:"+file
        finalRtmp = rtmp+" app=vod"+key+" playpath="+playPath+" swfUrl="+swfPlayer+" pageUrl="+link
        logger.debug("rtmp decoded link is: "+finalRtmp)
        return finalRtmp

    @staticmethod
    def decodeGamovideo(link):
        html = Downloader.getContentFromUrl(url=link)
        logger.debug(html)
        extracted = Decoder.extract("rtmp://",'"',html)
        logger.debug("extracted is: "+extracted)
        split = extracted.split('mp4:')
        extracted = split[0]+'mp4:'+split[1]
        logger.debug(str(len(split)))
        extracted = extracted.replace('_n?','_n.mp4?')
        link = "rtmp://"+extracted.replace("/mp4"," playpath=mp4")+" pageUrl="+link+" swfUrl=http://gamovideo.com/player61/jwplayer.flash.swf live=1"
        return link

    @staticmethod
    def decodeNowvideo(link):
        html = Decoder.getContent(link,'').read()
        stepkey = Decoder.extract('<input type="hidden" name="stepkey" value="','"',html)
        submit = Decoder.extract('<button type="submit" name="submit" class="btn" value="submit">','</button>',html).replace("+"," ")
        form = {'stepkey':stepkey,'submit':submit}
        html = Decoder.getContent(link,form,'','',True).read()

        file = Decoder.extract('flashvars.file="','"',html)
        fileKey = Decoder.extract('flashvars.filekey=',';',html)
        urlKey = Decoder.extract('var '+fileKey+'="','"',html)

        link2 = "http://www.nowvideo.sx/api/player.api.php?cid=1&key="+urlKey+"&cid2=undefined&pass=undefined&numOfErrors=0&file="+file+"&cid3=nowvideo&user=undefined&pass=undefined"
        html = Decoder.getContent(link2,'','http://www.nowvideo.sx/player/cloudplayer.swf').read()
        mp4File = Decoder.extract("=","&",html)

        logger.info('found link: '+mp4File)
        return mp4File


    @staticmethod
    def decodeFlashx(link):
        html = Decoder.getFinalHtmlFromLink(link) #has common attributes in form with streamcloud and others
        mp4File = ""
        for line in html.split("<script type='text/javascript'>"):
            if "eval(function(p,a,c,k,e,d)" in line:
                try:
                    encodedMp4File = Decoder.extract("eval(function(p,a,c,k,e,d)","</script>",html)
                    logger.debug("extracted code is: "+encodedMp4File)
                except:
                    pass
                mp4File += jsunpack.unpack(encodedMp4File) #needs un-p,a,c,k,e,t|d
                logger.debug("At this moment mp4 script is: "+mp4File)
        if mp4File.find("http://play.")>-1:
            mp4File = Decoder.extractWithRegex("http://play.",".mp4",mp4File)
        logger.debug("decoded mp4 file is: "+mp4File)
        return mp4File+"|"+Downloader.getHeaders()

    @staticmethod
    def decodePowvideo(link):
        html = Decoder.getFinalHtmlFromLink(link) #has common attributes in form with streamcloud and others
        logger.debug(html)
        try:
            encodedMp4File = Decoder.extract("<script type='text/javascript'>eval(function(p,a,c,k,e,d)","</script>",html)
        except:
            pass
        mp4File = jsunpack.unpack(encodedMp4File) #needs un-p,a,c,k,e,t|d
        mp4File = Decoder.rExtractWithRegex("http://",".mp4",mp4File)
        mp4File = mp4File.replace("\\","")
        logger.info('found mp4: '+mp4File)
        return mp4File



    @staticmethod
    def decodeStreamcloud(link):
        html = Decoder.getFinalHtmlFromLink(link) #has common attributes in form with powvideo and others
        mp4File = Decoder.extract('file: "','"',html)
        logger.info('found mp4: '+mp4File)
        return mp4File
        #return html

    @staticmethod
    def unwise(w, i, s, e): #javascript code, it's an obfuscation from www.caston.tv
        lIll = 0;
        ll1I = 0;
        Il1l = 0;
        ll1l = [];
        l1lI = [];
        while True:
            if (lIll < 5):
                l1lI.append(w[lIll])
            elif (lIll < len(w)):
                ll1l.append(w[lIll]);
            lIll+=1;
            if (ll1I < 5):
                l1lI.append(i[ll1I])
            elif (ll1I < len(i)):
                ll1l.append(i[ll1I])
            ll1I+=1;
            if (Il1l < 5):
                l1lI.append(s[Il1l])
            elif (Il1l < len(s)):
                ll1l.append(s[Il1l]);
            Il1l+=1;
            if (len(w) + len(i) + len(s) + len(e) == len(ll1l) + len(l1lI) + len(e)):
                break;
        lI1l = ''.join(ll1l)
        I1lI = ''.join(l1lI)
        ll1I = 0;
        l1ll = [];
        for lIll in range(0,len(ll1l),2):
            ll11 = -1;
            if ( ord(I1lI[ll1I]) % 2):
                ll11 = 1;
            l1ll.append(chr(    int(lI1l[lIll: lIll+2], 36) - ll11));
            ll1I+=1;
            if (ll1I >= len(l1lI)):
                ll1I = 0;
        ret=''.join(l1ll)
        if 'eval(function(w,i,s,e)' in ret:
            ret=re.compile('eval\(function\(w,i,s,e\).*}\((.*?)\)').findall(ret)[0]
            return Decoder.preWise(ret)
        else:
            return ret
        return ret

    @staticmethod
    def preWise(wised):
        value=""
        try:
            logger.debug("WISE -> extracting params...")
            paramsString = Decoder.rExtract("('","')",wised)
            logger.debug("WISE -> params extracted splitting...")
            params = paramsString.split(",")
            logger.info("WISE -> explit finished..."+str(len(params)))
            w = params[0].replace("'","")
            i = params[1].replace("'","")
            s = params[2].replace("'","")
            e = params[3].replace("'","")
            logger.debug("WISE -> launching main logic...")
            value=Decoder.unwise(w,i,s,e)
        except:
            logger.error("FATAL! It could not be dewised!")
        return value

    @staticmethod
    def resolveSimpleMath(form):
        if(form.find("(")>-1 and form.find(")")>-1):
            breaked = Decoder.extract("(",")",form)
            result = 0
            if breaked.find("+")>-1:
                first = int(breaked.split("+")[0])
                second = int(breaked.split("+")[1])
                result = first+second
            elif breaked.find("-")>-1:
                first = int(breaked.split("-")[0])
                second = int(breaked.split("-")[1])
                result = first-second
            elif breaked.find("*")>-1:
                first = int(breaked.split("*")[0])
                second = int(breaked.split("*")[1])
                result = first*second
            elif breaked.find("/")>-1:
                first = int(breaked.split("/")[0])
                second = int(breaked.split("/")[1])
                result = first/second

            if form.find(")")==len(form)-1:
                sign = form[form.find("(")-1]
                figure = form[:form.find("(")-2]
            else:
                sign = form[form.find(")")+1]
                figure = int(form[form.find(")")+2:])
            if sign=="+":
                form = str(figure+result)
            elif sign=="-":
                form = str(figure-result)
            elif sign=="*":
                form = str(figure*result)
            elif sign=="/":
                form = str(figure/result)
        return form

    @staticmethod
    def getUstreamLink(uStreamUrl,referer):
        logger.debug("Decoding ustream link: " + uStreamUrl)
        id = Decoder.extract('http://www.ustream.tv/embed/', "?", uStreamUrl)
        iphoneLink = "http://iphone-streaming.ustream.tv/uhls/" + id + "/streams/live/iphone/playlist.m3u8"
        logger.debug("iphoneLink is: " + iphoneLink)
        return iphoneLink  # TODO, get final rtmp link, but at this moment it's better than nothing else

    @staticmethod
    def getCastcampLink(code,referer=''):
        url = "http://www.castamp.com/embed.php?c="+code+"&tk=Gwsmev6F&vwidth=700&vheight=400"
        html = Downloader.getContentFromUrl(url=url,referer=referer)
        swfVer = "WIN/20,0,0,306"
        swfUrl = Decoder.extract("'flashplayer': \"","\"",html)
        rtmp = Decoder.extract("'streamer': '","'",html)
        file = Decoder.extract("'file': '", "'", html)
        filePrefix = Decoder.rExtract("'","'+unescape",html)
        replaceBy = Decoder.extract("replace('","'",html)
        replaced = Decoder.extract(replaceBy+"', '","'",html)
        unescaped = Decoder.extract("unescape('","'",html)
        escaped = urllib.unquote_plus(unescaped)
        playPath = filePrefix+escaped
        playPath = playPath.replace(replaceBy,replaced)
        logger.debug("file: "+file+" transformed to playpath: "+playPath)
        link = rtmp+" playpath="+playPath+" swfUrl="+swfUrl+" live=1 timeout=14 swfVfy=1 flashver="+swfVer+" pageUrl="+url
        return link

    @staticmethod
    def decodeStreamliveto(html,page=''):
        logger.debug("page referer which will be used: "+page)
        iframeUrl = "http://www.streamlive.to/embedplayer_new2.php?width=653&height=410&channel="+Decoder.extract('http://www.streamlive.to/embed/','&width=',html)+"&autoplay=true"
        html2 = Downloader.getContentFromUrl(url=iframeUrl,data="",cookie=Downloader.cookie,referer=page)
        if html2.find("Question:")>-1:#captcha
            logger.debug(html2)
            captcha = Decoder.rExtract(': ','<br /><br />',html2)
            if captcha.find("(")>-1:
                logger.debug("resolving captcha with math..."+captcha)
                try:
                    captcha = Decoder.resolveSimpleMath(captcha)
                except:
                    logger.error("Could not resolve captcha: "+captcha)
                    pass
            logger.debug("captcha="+captcha)
            captchaPost = urllib.urlencode({'captcha': captcha})
            logger.debug(captchaPost)
            time.sleep(4)
            html2 = Downloader.getContentFromUrl(url=iframeUrl,data=captchaPost,cookie=Downloader.cookie,referer=page)
        link = "https://www.github.com" # dummy url, f.i. ;)
        if "http://www.streamlive.to/player/ilive-plugin.swf" not in html2: #builds the link
            logger.debug("Next try: "+html2)
            if "antiware=" in Downloader.cookie:
                if " expires" in Downloader.cookie:
                    Downloader.cookie = Downloader.cookie[:Downloader.cookie.find(" expires")]
                    logger.debug("fix for cookie done!")
                logger.debug("trying second loop with new cookie: "+Downloader.cookie)
                #html2 = Downloader.getContentFromUrl(iframeUrl, "", "", page)
        if "http://www.streamlive.to/player/ilive-plugin.swf" in html2:  # builds the link
            swfUrl = "http://www.streamlive.to/player/ilive-plugin.swf"
            tokenUrl = Decoder.extractWithRegex("www.streamlive.to/server.php?id=", '"', html2)
            tokenUrl = tokenUrl[:(len(tokenUrl) - 1)]
            token = Downloader.getContentFromUrl("http://" + tokenUrl, "", Downloader.cookie, page)
            token = Decoder.extract('{"token":"', '"}', token)
            file = Decoder.extract('file: "', '",', html2).replace('.flv', '')
            streamer = Decoder.extract('streamer: "', '",', html2).replace("\\", "")
            link = streamer + "./" + file + " playpath=" + file + " live=1 token=" + token + " swfUrl=" + swfUrl + " pageUrl=http://www.streamlive.to/view" + (
            iframeUrl[iframeUrl.rfind("/"):])
            logger.debug("built a link to be used: " + link)
        else:
            logger.debug("Nothing done: " + html2)
        return link

    @staticmethod
    def decodeCastalbatv(url,page=''):
        channelId = url[url.find('cid=')+len('cid='):]
        if channelId.find("&")>-1:
            channelId = channelId[:channelId.find("&")]
        #iframeUrl = "http://castalba.tv/channel/"+channelId
        iframeUrl = url;
        logger.debug("using referer: "+page)
        html = Downloader.getContentFromUrl(iframeUrl,'',"",page)
        logger.debug("html is: "+html)
        file = "";
        if html.find(".m3u8")>-1:
            file = Decoder.rExtract("'file': '",'.m3u8',html)
            logger.debug("detected castalba file: "+file)
            if len(file)>0 and page!='':
                file+="|Referer="+page+("&User-Agent=Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0".replace(" ","+")) #TODO += Downloader.getHeaders(page)
            else:
                file+="|Referer="+file+("&User-Agent=Mozilla/5.0 (X11; Linux x86_64; rv:45.0) Gecko/20100101 Firefox/45.0".replace(" ","+")) #TODO += Downloader.getHeaders(page)
        else:
            if html.find("var file = '")>-1:
                file = Decoder.extract("var file = '","'",html)
                if 'file|' in html:
                    file = Decoder.extract("file|","'",html)
                    logger.debug("file was updated to: "+file)
            flash= Decoder.extract("'flashplayer': \"","\"",html)
            if html.find("return '/")>-1:
                rtmpUrl = "rtmp://"+Decoder.extract("return '/","';",html)
            elif "'streamer': " in html:
                line = Decoder.extract("'streamer': ", ",", html)
                methodName = Decoder.rExtract(' ', '()', line)
                logger.debug("Method target name: " + methodName)
                rtmpScript = Decoder.extract('function ' + methodName + '() {', '}', html)
                logger.debug("using script: "+rtmpScript)
                for scriptLine in rtmpScript.split("\n"):
                    if '/live' in scriptLine and '//' not in scriptLine:
                        scriptRtmp = Decoder.extract("'","'",scriptLine)
                        rtmpUrl = "rtmp://"+scriptRtmp
                        logger.debug("new rtmp is: " + rtmpUrl)
            else:
                rtmpUrl = "rtmp"+Decoder.rExtractWithRegex("://","/live';",html).replace("';","")
            playpath = file+"?"+Decoder.extract("unescape('?","'),",html)
            file = rtmpUrl+" app=live playpath="+playpath+" swfUrl="+flash+" pageUrl="+url+" flashver=WIN/2019,0,0,226 live=1"
        logger.debug("final link from castalba is: "+file)
        return file

    @staticmethod
    def getContent(url,data="",referer="",cookie="",dnt=True):
        logger.info('Using url: '+url)
        request = urllib2.Request(url)
        host = url[url.find("://")+3:]
        if host.find("/")>-1:
            host = host[:host.find("/")]
        logger.debug("Host: "+host)
        request.add_header("User-Agent", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36")
        if len(referer)>0:
            request.add_header("Referer", referer)
        if len(cookie)>0:
            request.add_header("Cookie", cookie)
        request.add_header("Accept-Language", "en-US,en;q=0.8,es-ES;q=0.5,es;q=0.3")
        request.add_header("Connection", "keep-alive")
        if dnt:
            request.add_header("DNT", "1")
        request.add_header("Host", host)

        form = urllib.urlencode(data)
        logger.debug("form: "+form)
        if len(form)>0:
            response = urllib2.urlopen(request,form)
        else:
            response = urllib2.urlopen(request)
        return response

    @staticmethod
    def getContent2(url, referer="",proxy=None, post=None):
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