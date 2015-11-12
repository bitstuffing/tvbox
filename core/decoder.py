import httplib
import urllib2
import urllib
import time
import re
import base64

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
        response = Decoder.getContent(link,'')
        data = response.read()
        html = ""
        if data.find("<script type='text/javascript'>eval(function(p,a,c,k,e")==-1:

            finalCookie = ""
            cookies = ";"
            cookies = response.info()['Set-Cookie']

            for cookie in cookies.split(";"):
                if cookie.find("path=") == -1 and cookie.find("expires=") == -1 and cookie.find("Max-Age=") and cookie.find("domain="):
                    if len(finalCookie)>0:
                        finalCookie += "; "
                    finalCookie+= cookie

            print 'Extracted cookie: '+finalCookie

            #build form
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
                html = Decoder.getContent(link,form,link,finalCookie,True).read()
        else:
            html = data

        return html

    @staticmethod
    def decodeBussinessApp(html,iframeReferer):
        response = ""
        if html.find('<input type="hidden" id="ssx1" value="')>-1:
            ssx1 = Decoder.extract('<input type="hidden" id="ssx1" value="','"',html)
            ssx4 = Decoder.extract('<input type="hidden" id="ssx4" value="','"',html)
            escaped = Decoder.extract("<script type='text/javascript'>document.write(unescape('","'",html)
            unescaped = urllib.unquote(escaped)
            decodedssx1 = base64.standard_b64decode(ssx1)
            decodedssx4 = base64.standard_b64decode(ssx4)
            #print "decoded{"+decodedssx1+","+decodedssx4+"} unescaped: "+unescaped
            app = decodedssx4[decodedssx4.find("vod/?token="):]
            iframeReferer = urllib.unquote_plus(iframeReferer.replace("+","@#@")).replace("@#@","+") #unquote_plus replaces '+' characters
            response = decodedssx4+" playpath="+decodedssx1+" app="+app+" swfUrl=http://www.businessapp1.pw/jwplayer5/addplayer/jwplayer.flash.swf token=@@stop-stole@@ flashver=WIN/2019,0,0,226 live=true timeout=15 pageUrl="+iframeReferer ##TODO, extract token from code "http://www.businessapp1.pw/jwplayer5/addplayer/jwplayer.js", last line
            print "to player: "+response
        else:
            playPath = ""
            rtmpValue = ""
            #i = 0
            for splittedHtml in html.split('<input type="hidden" id="'):
                if splittedHtml.find("DOCTYPE html PUBLIC")==-1 and splittedHtml.find(' value=""')==-1:
                    print "processing hidden: "+splittedHtml
                    extracted = splittedHtml[splittedHtml.find('value="')+len('value="'):]
                    extracted = extracted[0:extracted.find('"')]
                    print "extracted hidden value: "+extracted
                    if playPath == "":
                        playPath = base64.standard_b64decode(extracted)
                    else:
                        rtmpValue = base64.standard_b64decode(extracted)
                    print "original: "+extracted+", extracted: "+base64.standard_b64decode(extracted)
                #i+=1
            if rtmpValue.find("vod/?token=")>-1:
                app = rtmpValue[rtmpValue.find("vod/?token="):]
                iframeReferer = urllib.unquote_plus(iframeReferer.replace("+","@#@")).replace("@#@","+") #unquote_plus replaces '+' characters
                response = rtmpValue+" playpath="+playPath+" app="+app+" swfUrl=http://www.businessapp1.pw/jwplayer5/addplayer/jwplayer.flash.swf token=@@stop-stole@@ flashver=WIN/2019,0,0,226 live=true timeout=15 pageUrl="+iframeReferer ##TODO, extract token from code "http://www.businessapp1.pw/jwplayer5/addplayer/jwplayer.js", last line
            else:
                app = "redirect"+rtmpValue[rtmpValue.find("?token=play@"):]
                #response = rtmpValue+" playpath="+playPath+" app="+app+" swfUrl=http://www.businessapp1.pw/jwplayer5/addplayer/jwplayer.flash.swf token=@@stop-stole@@ flashver=WIN/2019,0,0,226 live=true timeout=15 pageUrl="+iframeReferer
                response = rtmpValue+" playpath="+playPath+" app="+app+" swfUrl=http://www.businessapp1.pw/jwplayer5/addplayer/jwplayer.flash.swf flashver=WIN/2019,0,0,226 token=@@stop-stole@@ live=true timeout=15 pageUrl="+iframeReferer
                #response = rtmpValue+" playpath="+playPath+" swfUrl=http://www.businessapp1.pw/jwplayer5/addplayer/jwplayer.flash.swf flashver=WIN/2019,0,0,226 live=true timeout=15 pageUrl="+iframeReferer
        return response


    @staticmethod
    def decodeThevideo(link):
        html = Decoder.getFinalHtmlFromLink(link,5,True)
        mp4Link = Decoder.rExtract(", file: '","'",html) #there are more qualities, so I get the last one which is the best of
        mp4Link = mp4Link[0:mp4Link.find("'")]
        print "found link: "+mp4Link
        return mp4Link

    @staticmethod
    def decodeStreamin(link):
        html = Decoder.getFinalHtmlFromLink(link,5)
        mp4File = Decoder.extract("config:{file:'","'",html)
        print 'found link: '+mp4File
        return mp4File

    @staticmethod
    def decodeGamovideo(link):
        html = Decoder.getContent(link,'').read()
        try:
            encodedMp4File = Decoder.extract("<script type='text/javascript'>eval(function(p,a,c,k,e,d)","</script>",html)
        except:
            print html
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

        print 'found link: '+mp4File
        return mp4File


    @staticmethod
    def decodeFlashx(link):
        html = Decoder.getFinalHtmlFromLink(link) #has common attributes in form with streamcloud and others
        try:
            encodedMp4File = Decoder.extract("<script type='text/javascript'>eval(function(p,a,c,k,e,d)","</script>",html)
        except:
            print html
        mp4File = jsunpack.unpack(encodedMp4File) #needs un-p,a,c,k,e,t|d
        mp4File = Decoder.extractWithRegex("http://play.",".mp4",mp4File)
        return mp4File

    @staticmethod
    def decodePowvideo(link):
        html = Decoder.getFinalHtmlFromLink(link) #has common attributes in form with streamcloud and others
        try:
            encodedMp4File = Decoder.extract("<script type='text/javascript'>eval(function(p,a,c,k,e,d)","</script>",html)
        except:
            print html
        mp4File = jsunpack.unpack(encodedMp4File) #needs un-p,a,c,k,e,t|d
        mp4File = Decoder.rExtractWithRegex("http://",".mp4",mp4File)
        mp4File = mp4File.replace("\\","")
        print 'found mp4: '+mp4File
        return mp4File



    @staticmethod
    def decodeStreamcloud(link):
        html = Decoder.getFinalHtmlFromLink(link) #has common attributes in form with powvideo and others
        #print 'html returned: '+html
        mp4File = Decoder.extract('file: "','"',html)
        print 'found mp4: '+mp4File
        return mp4File
        #return html

    @staticmethod
    def getContent(url,data="",referer="",cookie="",dnt=True):
        print 'Using url: '+url
        request = urllib2.Request(url)
        host = url[url.find("://")+3:]
        host = host[:host.find("/")]
        print "Host: "+host
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
        print "form: "+form
        if len(form)>0:
            response = urllib2.urlopen(request,form)
        else:
            response = urllib2.urlopen(request)
        return response
