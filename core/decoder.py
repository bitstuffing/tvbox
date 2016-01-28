import httplib
import urllib2
import urllib
import time
import re
import base64
from core import logger
from core.downloader import Downloader
try:
    import json
except:
    import simplejson as json
from core import jsunpack

class Decoder():

    @staticmethod
    def decodeLink(link):
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
        elif link.find("://openload")>-1:
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

        return link

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
        data = Downloader.getContentFromUrl(link,"","lang=english")
        html = ""
        if data.find("<script type='text/javascript'>eval(function(p,a,c,k,e")==-1:

            finalCookie = "lang=english"
            '''
            cookies = ";"
            cookies = response.info()['Set-Cookie']

            for cookie in cookies.split(";"):
                if cookie.find("path=") == -1 and cookie.find("expires=") == -1 and cookie.find("Max-Age=") and cookie.find("domain="):
                    if len(finalCookie)>0:
                        finalCookie += "; "
                    finalCookie+= cookie

            logger.info('Extracted cookie: '+finalCookie)
            '''
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
        logger.info("decoded url is: "+decodedFlashvars)
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
        file = Decoder.extract('file:"','",',html)
        logger.debug("found file: "+file)
        return file

    @staticmethod
    def decodeOpenload(link):
        #get cookies
        mediaId = Decoder.extract("/f/","/",link)
        embedUrl = 'https://openload.io/embed/'+mediaId
        html = Downloader.getContentFromUrl(embedUrl,"","","",False,False)
        logger.info("html is: "+html)
        logger.debug("using cookie 1: "+Downloader.cookie)
        logger.debug("Media id for openload is: "+mediaId)
        extra = "&login=f750b26513f64034&key=oaA-MbZo" #this avoid captcha petition
        link2 = "https://api.openload.io/1/file/dlticket?file="+mediaId+extra
        data = Downloader.getContentFromUrl(link2,"",Downloader.cookie,embedUrl,True,False)
        logger.debug("jsonData: "+data)
        js_result = json.loads(data)
        logger.info("sleeping... "+str(js_result['result']['wait_time']))
        time.sleep(int(js_result['result']['wait_time']))
        link3 = 'https://api.openload.io/1/file/dl?file=%s&ticket=%s' % (mediaId, js_result['result']['ticket'])
        logger.debug("using cookie 2: "+Downloader.cookie)
        result = Downloader.getContentFromUrl(link3,"",Downloader.cookie,embedUrl,True,False)
        logger.debug("jsonData 2: "+result)
        js_result2 = json.loads(result)
        file = js_result2['result']['url'] + '?mime=true'
        logger.info("Built final link: "+file)
        return file

    @staticmethod
    def decodePrivatestream(html,referer):
        rtmpUrl = "rtmp://31.220.40.63/privatestream/"
        logger.info("trying to get playpath from html...")
        if html.find("var v_part = '")>-1:
            logger.info("detected playpath...")
            playPath = Decoder.extract("var v_part = '","';",html)[len("/privatestream/"):]
            swfUrl = "http://privatestream.tv/js/jwplayer.flash.swf"
            rtmpUrl = rtmpUrl+playPath+" playPath="+playPath+" swfUrl="+swfUrl+" live=1 timeout=12 pageUrl="+referer
            logger.info("final link:"+rtmpUrl)
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
        logger.info("brute params are: "+param)
        firstArgument = Decoder.extract('s=','&',param)
        id = Decoder.extract('id=','&',param)
        pk = param[param.find('pk=')+len('pk='):]
        newParam = firstArgument+"?id="+id+"&pk="+pk #format param
        logger.info("param is now: "+newParam)
        return newParam

    @staticmethod
    def decodeLiveFlash(html,referer):
        newParam = Decoder.extractParams(html)
        finalUrl = "rtmp://46.165.196.40/stream playPath="+newParam+" swfVfy=1 timeout=10 conn=S:OK live=true swfUrl=http://www.liveflashplayer.net/resources/scripts/fplayer.swf flashver=WIN/2019,0,0,226 pageUrl="+referer
        return finalUrl

    @staticmethod
    def decodeUcaster(html,referer):
        newParam = Decoder.extractParams(html)
        finalUrl = "rtmp://46.28.50.116/live/ playPath="+newParam+" swfVfy=1 timeout=10 conn=S:OK live=true swfUrl=http://www.embeducaster.com/static/scripts/fplayer.swf flashver=WIN/2019,0,0,226 pageUrl="+referer
        return finalUrl

    @staticmethod
    def extractSawlive(scriptSrc,cookie,iframeUrl):
        encryptedHtml = Downloader.getContentFromUrl(scriptSrc,"",cookie,iframeUrl)
        #print encryptedHtml
        decryptedUrl = Decoder.decodeSawliveUrl(encryptedHtml)
        html3 = Downloader.getContentFromUrl(decryptedUrl,"",cookie,scriptSrc)
        #ok, now extract flash script content

        flashContent = Decoder.extract("var so = new SWFObject('","</script>",html3)
        file = Decoder.extract("'file', '","');",flashContent)
        rtmpUrl = ""
        if flashContent.find("'streamer', '")>.1:
            rtmpUrl = Decoder.extract("'streamer', '","');",flashContent)
        swfUrl = "http://static3.sawlive.tv/player.swf" #default
        #update swf url
        swfUrl = flashContent[:flashContent.find("'")]
        logger.info("updated swf player to: "+swfUrl)
        if rtmpUrl=='' and file.find("http://")>-1:
            finalRtmpUrl = file #it's a redirect with an .m3u8, so it's used
        else:
            finalRtmpUrl = rtmpUrl+" playpath="+file+" swfUrl="+swfUrl+" live=1 conn=S:OK pageUrl="+decryptedUrl+" timeout=12"
        return finalRtmpUrl

    @staticmethod
    def decodeSawliveUrl(encryptedHtml):
        #first extract var values and append it to an array
        varPart = encryptedHtml[0:encryptedHtml.find(';document.write')]
        vars = {}
        for varElement in varPart.split('var '): #loop each var
            if varElement.find('=')>-1:
                bruteElement = varElement.split('=')
                extractedElement = Decoder.extract("'","'",bruteElement[1])
                #logger.info("obtained key: "+bruteElement[0]+", with value: "+extractedElement)
                vars[bruteElement[0]] = extractedElement
		if extractedElement.find("+")>-1:
			for currentVarSubElement in extractedElement.split("+"):
				if len(currentVarSubElement)>0 and currentVarSubElement.find('"')==-1:
					logger.info("using var: "+currentVarSubElement)
					preSubFix = "var "+currentVarSubElement+"=";
					valueInternalVar = varPart[varPart.find(preSubFix)+len(preSubFix)+1:]
					logger.info("Internal var provisional is: "+valueInternalVar)
					valueInternalVar = valueInternalVar[:valueInternalVar.find('"')]
					logger.info("Internal var final is: "+valueInternalVar)
        #second extract src part for a diagnostic
        bruteSrc = Decoder.extract(' src="','"></iframe>',encryptedHtml)
        finalUrl = ""
        if bruteSrc.find("+")>-1:
            for bruteUrlPart in bruteSrc.split("+"):
                if bruteUrlPart.find("unescape")>-1:
                    extractedValue = Decoder.extract("(",")",bruteUrlPart)
                    if extractedValue.find("'")>-1: #it means encoded html
                        extractedValue = Decoder.extract("'","'",extractedValue)
			logger.info("1")
                        finalUrl += urllib.unquote(extractedValue)
                    else: #it means a var, seek it
                        if vars.has_key(extractedValue):
                            finalUrl += vars[extractedValue]
			    logger.info("2")
                else:
                    if bruteUrlPart.find("'")==0:#there is a var
                        if vars.has_key(bruteUrlPart):
                            finalUrl += vars[bruteUrlPart]
			    logger.info("3")
                        else:
                            bruteUrlPart = bruteUrlPart.replace("'","")
                            finalUrl+=bruteUrlPart
			    logger.info("4")
                            #logger.info("brute text included1: "+bruteUrlPart)
                    else: #brute text, paste it without the final "'" if it contains that character
                        bruteUrlPart = bruteUrlPart.replace("'","")
                        if vars.has_key(bruteUrlPart):
			    logger.info("5"+bruteUrlPart+","+vars[bruteUrlPart])
			    if vars[bruteUrlPart].find('"')==-1:
			        finalUrl += vars[bruteUrlPart]
			    else:
			        for bruteUrlPart2 in vars[bruteUrlPart].split("+"):
					logger.info("seek key: "+bruteUrlPart2)
					if vars.has_key(bruteUrlPart2) and bruteUrlPart2.find('"')==-1:
						finalUrl += vars[bruteUrlPart2].replace('"',"")
                        else:
                            finalUrl+=bruteUrlPart
                            logger.info("brute text included2: "+bruteUrlPart)
                logger.info("now finalUrl is: "+urllib.unquote(finalUrl))
        finalUrl = urllib.unquote(finalUrl) #finally translate to good url
        if finalUrl.find("unezcapez(")>-1:
            logger.info("replacing url new encoding...")
            finalUrl = finalUrl.replace("unezcapez(","").replace(')','') #little fix for new coding, it will be included in the previews revision
        logger.info("Decrypted url is: "+finalUrl)
        return finalUrl

    @staticmethod
    def decodeLetonTv(html,referer):
        rtmpUrl = "rtmp://31.200.0.186"
        logger.info("trying to get playpath from html...")
        if html.find("var v_part = '")>-1:
            logger.info("detected playpath...")
            playPath = Decoder.extract("var v_part = '","';",html)
            swfUrl = "http://files.leton.tv/jwplayer.flash.swf"
            rtmpUrl = rtmpUrl+playPath+" playPath="+playPath+" swfUrl="+swfUrl+" live=1 timeout=12 pageUrl="+referer
        else:
            logger.info("nothing detected, returning incomplete link :(")
        return rtmpUrl

    @staticmethod
    def decodeBussinessApp(html,iframeReferer):
        #print html
        response = ""

        jsFile = "http://www.businessapp1.pw/jwplayer5/addplayer/jwplayer.js"
        if html.find("jwplayer5/addplayer/jwplayer.js")>-1:
            jsFile = Decoder.rExtractWithRegex("http://","jwplayer5/addplayer/jwplayer.js",html)
            logger.info("updated js player to: "+jsFile)
        elif html.find("http://www.playerhd1.pw")>-1:
            jsFile = "http://www.playerhd1.pw/jwplayer5/addplayer/jwplayer.js"
        token = ""
        try:
            token = Decoder.extractBusinessappToken(iframeReferer,jsFile)
        except:
            logger.error("Error, trying without token")
            pass

        swfUrl = "http://www.businessapp1.pw/jwplayer5/addplayer/jwplayer.flash.swf"
        if html.find("jwplayer5/addplayer/jwplayer.flash.swf")>-1: #http://www.playerapp1.pw/jwplayer5/addplayer/jwplayer.flash.swf
            swfUrl = Decoder.rExtractWithRegex("http://","jwplayer5/addplayer/jwplayer.flash.swf",html)
            logger.info("updated swf player to: "+swfUrl)
        elif jsFile.find("businessapp1.pw")==-1:
            swfUrl = "http://"+Decoder.extract('//',"/",jsFile)+"/jwplayer5/addplayer/jwplayer.flash.swf"
            logger.info("updated swf player to: "+swfUrl)
        elif html.find("http://www.playerhd1.pw")>-1:
            swfUrl = "http://www.playerhd1.pw/jwplayer5/addplayer/jwplayer.flash.swf"

        if html.find('<input type="hidden" id="ssx1" value="')>-1:
            ssx1 = Decoder.extract('<input type="hidden" id="ssx1" value="','"',html)
            ssx4 = Decoder.extract('<input type="hidden" id="ssx4" value="','"',html)
            escaped = Decoder.extract("<script type='text/javascript'>document.write(unescape('","'",html)
            unescaped = urllib.unquote(escaped)
            decodedssx1 = base64.standard_b64decode(ssx1)
            decodedssx4 = base64.standard_b64decode(ssx4)
            #print "decoded{"+decodedssx1+","+decodedssx4+"} unescaped: "+unescaped
            iframeReferer = urllib.unquote_plus(iframeReferer.replace("+","@#@")).replace("@#@","+") #unquote_plus replaces '+' characters
            if decodedssx4.find(".m3u8")>-1:
                logger.info("Found simple link: "+decodedssx4)
                response = Decoder.getContent(decodedssx4,"",iframeReferer).read()
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
                logger.info("link1: "+decodedssx1)
                logger.info("link2: "+decodedssx4)
            logger.info("to player: "+response)
        else:
            playPath = ""
            rtmpValue = ""
            #i = 0
            finalSimpleLink = ""
            for splittedHtml in html.split('<input type="hidden" id="'):
                if splittedHtml.find("DOCTYPE html PUBLIC")==-1 and splittedHtml.find(' value=""')==-1:
                    #logger.info("processing hidden: "+splittedHtml)
                    extracted = splittedHtml[splittedHtml.find('value="')+len('value="'):]
                    extracted = extracted[0:extracted.find('"')]
                    logger.info("extracted hidden value: "+extracted)
                    if playPath == "":
                        playPath = base64.standard_b64decode(extracted)
                    else:
                        rtmpValue = base64.standard_b64decode(extracted)
                    decodedAndExtracted = base64.standard_b64decode(extracted)
                    logger.info("original: "+extracted+", extracted: "+decodedAndExtracted)
                    if decodedAndExtracted.find(".m3u8")>-1:
                        finalSimpleLink = decodedAndExtracted
                #i+=1
            if finalSimpleLink!="":
                logger.info("Found simple link: "+finalSimpleLink)
                response = Decoder.getContent(finalSimpleLink,"",iframeReferer).read()
                if response.find("chunklist.m3u8")>-1:
                    finalSimpleLink2 = finalSimpleLink[:finalSimpleLink.rfind("/")+1]+"chunklist.m3u8"
                    response = Decoder.getContent(finalSimpleLink2,"",iframeReferer).read()
                    logger.debug("response for m3u8(a): "+response)
                    response = finalSimpleLink2+"|Referer="+iframeReferer
                else:
                    logger.debug("response for m3u8(b): "+response)
                    response = finalSimpleLink
            elif rtmpValue.find("vod/?token=")>-1:
                app = rtmpValue[rtmpValue.find("vod/?token="):]
                iframeReferer = urllib.unquote_plus(iframeReferer.replace("+","@#@")).replace("@#@","+") #unquote_plus replaces '+' characters
                token = Decoder.extractBusinessappToken(iframeReferer,jsFile)
                response = rtmpValue+" playpath="+playPath+" app="+app+" swfUrl="+swfUrl+" token="+token+" flashver=WIN/2019,0,0,226 live=true timeout=14 pageUrl="+iframeReferer
            else:
                app = "redirect"+rtmpValue[rtmpValue.find("?token=play@"):]
                token = Decoder.extractBusinessappToken(iframeReferer,jsFile)
                response = rtmpValue+" playpath="+playPath+" app="+app+" swfUrl="+swfUrl+" token="+token+" flashver=WIN/2019,0,0,226 live=true timeout=14 pageUrl="+iframeReferer
        return response

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
        html = Decoder.getFinalHtmlFromLink(link,5)
        mp4File = Decoder.extract("config:{file:'","'",html)
        logger.info('found link: '+mp4File)
        return mp4File

    @staticmethod
    def decodeGamovideo(link):
        html = Decoder.getContent(link,'').read()
        try:
            encodedMp4File = Decoder.extract("<script type='text/javascript'>eval(function(p,a,c,k,e,d)","</script>",html)
        except:
            pass
            #print html
        mp4File = jsunpack.unpack(encodedMp4File) #needs un-p,a,c,k,e,t|d
        ip = Decoder.extract("http://",'/',mp4File)
        #port = Decoder.extract(":","/",ip)
        #ip = ip[0:ip.find("/")]
        code = Decoder.extract("mp4?h=",'"',mp4File)
        link = "http://"+ip+"/"+code+"/v.mp4"

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
        try:
            encodedMp4File = Decoder.extract("<script type='text/javascript'>eval(function(p,a,c,k,e,d)","</script>",html)
        except:
            pass
            #print html
        mp4File = jsunpack.unpack(encodedMp4File) #needs un-p,a,c,k,e,t|d
        mp4File = Decoder.extractWithRegex("http://play.",".mp4",mp4File)
        return mp4File

    @staticmethod
    def decodePowvideo(link):
        html = Decoder.getFinalHtmlFromLink(link) #has common attributes in form with streamcloud and others
        try:
            encodedMp4File = Decoder.extract("<script type='text/javascript'>eval(function(p,a,c,k,e,d)","</script>",html)
        except:
            pass
            #print html
        mp4File = jsunpack.unpack(encodedMp4File) #needs un-p,a,c,k,e,t|d
        mp4File = Decoder.rExtractWithRegex("http://",".mp4",mp4File)
        mp4File = mp4File.replace("\\","")
        logger.info('found mp4: '+mp4File)
        return mp4File



    @staticmethod
    def decodeStreamcloud(link):
        html = Decoder.getFinalHtmlFromLink(link) #has common attributes in form with powvideo and others
        #print 'html returned: '+html
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
            logger.info("WISE -> extracting params...")
            paramsString = Decoder.rExtract("('","')",wised)
            logger.info("WISE -> params extracted splitting...")
            params = paramsString.split(",")
            logger.info("WISE -> explit finished..."+str(len(params)))
            w = params[0].replace("'","")
            i = params[1].replace("'","")
            s = params[2].replace("'","")
            e = params[3].replace("'","")
            logger.info("WISE -> launching main logic...")
            value=Decoder.unwise(w,i,s,e)
        except:
            logger.error("FATAL! It could not be dewised!")
        return value

    @staticmethod
    def getContent(url,data="",referer="",cookie="",dnt=True):
        logger.info('Using url: '+url)
        request = urllib2.Request(url)
        host = url[url.find("://")+3:]
        if host.find("/")>-1:
            host = host[:host.find("/")]
        logger.info("Host: "+host)
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
        logger.info("form: "+form)
        if len(form)>0:
            response = urllib2.urlopen(request,form)
        else:
            response = urllib2.urlopen(request)
        return response