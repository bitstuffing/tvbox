import httplib
import urllib
from core.decoder import Decoder
from core import logger
from core import jsunpack
from providers.filmoncom import Filmoncom
from providers.live9net import Live9net
from core.downloader import Downloader

class Cricfreetv(Downloader):

    cookie = ""
    MAIN_URL = "http://cricfree.tv/"

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == "0":
            html = Cricfreetv.getContentFromUrl(Cricfreetv.MAIN_URL)
            element = {}
            element["link"] = '1'
            element["title"] = 'Display by event'
            x.append(element)
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
        elif str(page) == '1': #event
            html = Cricfreetv.getContentFromUrl(Cricfreetv.MAIN_URL)
            html = Decoder.extract('<section class="panel">',"</section>",html)
            for htmlElement in html.split('<td><span class="sport-icon'):
                if htmlElement.find('</span></td>\n<td>')>-1:
                    name = Decoder.rExtract('</span></td>\n<td>',"</td>\n<td style=\"color:#545454;",htmlElement)
                    event = Decoder.rExtract(' target="_blank">',"</a></td>",htmlElement)
                    time = Decoder.extract('<td class="matchtime" style="color:#545454;font-weight:bold;font-size: 9px">','</td>',htmlElement)
                    href = Decoder.extract(' href="','"',htmlElement)
                    element = {}
                    element["title"] = time+" - "+name+" - "+event
                    element["link"] = href
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
        if firstScriptUrl.find('"')>-1:
            firstScriptUrl = firstScriptUrl[0:firstScriptUrl.find('"')]
        scriptUrl = Cricfreetv.extractScriptIframeUrl(html,firstScriptUrl,referer)
        logger.info("level 2, scriptUrl: "+scriptUrl+", cookie: "+Cricfreetv.cookie)
        lastIframeHtml = Cricfreetv.getContentFromUrl(scriptUrl,"",Cricfreetv.cookie,iframeUrl)
        #print lastIframeHtml
        file = Cricfreetv.seekIframeScript(lastIframeHtml,iframeUrl,scriptUrl)
        logger.info("script logic finished!")
        return file

    @staticmethod
    def seekIframeScript(html,referer, iframeUrl):
        lastIframeHtml = html
        file = ""
        logger.info("seek iframe logic... ")
        if html.find("http://theactionlive.com/live")>-1:
            file = Cricfreetv.launchScriptLogic("http://theactionlive.com/live",html,referer,iframeUrl)
        elif html.find('http://biggestplayer.me/play')>-1:
            file = Cricfreetv.launchScriptLogic("http://biggestplayer.me/play",html,referer,iframeUrl)
        elif html.find("http://www.yotv.co/play")>-1:
            file = Cricfreetv.launchScriptLogic("http://www.yotv.co/play",html,referer,iframeUrl)
        elif html.find("http://www.yocast.tv/embed")>-1:
            file = Cricfreetv.launchScriptLogic("http://www.yocast.tv/embed",html,referer,iframeUrl)
        elif html.find("http://www.rocktv.co/play")>-1:
            file = Cricfreetv.launchScriptLogic("http://www.rocktv.co/play",html,referer,iframeUrl)
        elif html.find("http://miplayer.net/embed")>-1:
            file = Cricfreetv.launchScriptLogic("http://miplayer.net/embed",html,referer,iframeUrl)
        elif html.find("http://www.filmon.com/tv/")>-1:
            url = Decoder.extractWithRegex("http://www.filmon.com/tv/",'"',html).replace('"',"")
            logger.info("using first filmon.com url from provider, url: "+url+", r: "+referer)
            file = Filmoncom.launchScriptLogic(url,referer)[0]["url"]
        elif html.find('file: "http')>-1: #found final link
            file = Decoder.extract('file: "','"',html)
            logger.info("found final link: "+file)
        elif html.find('securetoken:')>-1:
            logger.info("building final link...")
            file = Decoder.extract('file: "','"',html)
            securetoken = Decoder.extract('securetoken: "','"',html)
            #print html
            flashPlayer = 'http://p.jwpcdn.com/6/12/jwplayer.flash.swf'
            rtmpUrl = file[0:file.rfind('/')+1]+" playpath="+file[file.rfind('/')+1:]+" token="+securetoken+" swfUrl="+flashPlayer+" live=1 timeout=13 pageUrl="+iframeUrl
            logger.info("found final link: "+rtmpUrl)
            file = rtmpUrl
        elif html.find('return(["r","t","m","p"')>-1:
            swfUrl = "http://cdn.ibrod.tv/player/jwplayer.flash.swf"
            bruteData = Decoder.extract('return(["r","t","m","p"',"</script>",html)
            line = bruteData[:bruteData.find(');')]
            rtmp = "rtmp:"+Decoder.extract("return([","].join(",line).replace('","',"").replace('"','').replace('\\',"")
            bruteVar = Decoder.extract('].join("") + ',".join("") + ",line)
            splitter = "var "+bruteVar+" = ["
            if html.find(splitter)>-1:
                arrayContent = Decoder.extract(splitter,"];",html).replace('"',"").replace(',',"")
                #rtmp += arrayContent
            if line.find('document.getElementById("')>-1:
                element = Decoder.extract('document.getElementById("','").',line)
                span = Decoder.extract('id='+element+'>','</span>',html) #it doesn't need decode
                #rtmp += span

            playpath = Decoder.rExtract('return([','].join(""));',bruteData).replace('","',"").replace('"','').replace('\\',"")
            file = rtmp+" playpath="+playpath+" timeout=12 live=1 swfUrl="+swfUrl+" pageUrl="+iframeUrl
            logger.info("Built a rtmp with data: "+file)
        elif html.find("eval(unescape('")>-1:
            html = Cricfreetv.decodeContent(html).lower()
        elif html.find('<a href="http://sports4u.tv/channel')>-1 or html.find('http://sports4u.tv/embed/')>-1:
            if html.find('http://sports4u.tv/embed/')>-1:
                urlLink = Decoder.extractWithRegex('http://sports4u.tv/embed/','"',html).replace('"',"")
            elif html.find('<a href="http://sports4u.tv/channel')>-1:
                logger.info("urlLink...")
                urlLink = Decoder.extractWithRegex('<a href="http://sports4u.tv/channel','/"',html)
                logger.info("urlLink2..."+urlLink)
                urlLink = urlLink[urlLink.find('"')+1:urlLink.rfind('"')]
                logger.info("urlLinkFinal..."+urlLink)
                if urlLink != iframeUrl:
                    html2 = Cricfreetv.getContentFromUrl(urlLink,"",Cricfreetv.cookie,iframeUrl)
                    #print html2
                    file = Cricfreetv.seekIframeScript(html2,iframeUrl,urlLink)
                    if file=='':
                        #extract iframe value
                        iframe = Decoder.extract('<iframe frameborder="0" marginheight="0" marginWidth="0" height="490" id="iframe" src="','" id="',html).replace('"',"")
                        file = Cricfreetv.extractIframeValue(iframe,html,referer)
        else:
            if html.find('<iframe id="player" scrolling="no" width="620" height="490" allowtransparency="no" frameborder="0" src="')>-1:
                iframe = Decoder.extract('<iframe id="player" scrolling="no" width="620" height="490" allowtransparency="no" frameborder="0" src="','"',html)
                file = Cricfreetv.extractIframeValue(iframe,html,referer)
            elif html.find('<iframe ')>-1: #brute method forced
                logger.info("brute method launched...")
                iframe = Decoder.rExtract('<iframe ','</iframe>',html)
                iframe = Decoder.extract('src="','"',iframe)
                file = Cricfreetv.extractIframeValue(iframe,html,referer)
            else:
                print html

        return file

    @staticmethod
    def extractIframeValue(iframe,html,referer):
        file = ""
        if iframe.find("http:")!=0:
            iframe = Decoder.extract("<iframe src='","' ",html).replace("'","") #take into account .lower() characters, so is not ' SRC=
            if iframe.find("http:")!=0:
                iframe = Decoder.extract(' src="','"',html).replace('"',"")
        logger.info("using iframeUrl: "+iframe)
        if iframe.find("filmon.")>-1: # i prefer this fix to change all logic, really, I boried about this provider and is a 'silly' provider
            logger.info("Detected exceptional filmon.com|tv provider: "+iframe)
            file = Filmoncom.launchScriptLogic(iframe,referer)[0]["url"]
        else:
            html2 = Cricfreetv.getContentFromUrl(iframe,"",Cricfreetv.cookie,referer)
            #print html2
            if html2.find("http://www3.sawlive.tv/embed/")>-1:
                iframe2 = Decoder.extractWithRegex("http://www3.sawlive.tv/embed/",'"',html2).replace('"',"")
                logger.info("detected a sawlive: "+iframe2+", from: "+iframe)
                #file = Live9net.getChannels(iframe2) #Live9net has the sawlive decoder, so it decodes target link
                file = Decoder.extractSawlive(iframe2,Cricfreetv.cookie,iframe)
            else:
                file = Cricfreetv.seekIframeScript(html2,referer,iframe)
        return file

    @staticmethod
    def decodeContent(html): #This method is used to fix a "probably" encoding/decoding problem from provider
        #new encoded iframe method
        logger.info("trying new method for encrypted javascript code...")
        html2 = Decoder.extractWithRegex("eval(unescape('","'));",html)
        html3 = Decoder.rExtractWithRegex("eval(unescape('","'));",html)
        html3 = html3.replace("eval(","").replace("unescape(","").replace(" + ","").replace(")","").replace("'","").replace(";","")
        logger.info("extracted code is: "+html3)
        decodedHtml = urllib.unquote(html2[:html2.find(";")+1]).decode('utf8')
        logger.info("decypter function in javascript is: "+decodedHtml)
        encryptedCall = urllib.unquote(html3).decode('utf8')
        #encryptedCall = html3
        logger.info("final html is: "+encryptedCall)
        #now extract encrypted string
        encryptedCall = Decoder.extract("('","'));",encryptedCall)
        splitter = Decoder.extract('s.split("','");',decodedHtml)
        logger.info("splitter: "+splitter)
        subfixer = Decoder.extract('tmp[1] + "','");',decodedHtml)
        logger.info("subfixer: "+subfixer)
        s = encryptedCall.split(splitter)[0]
        k = encryptedCall.split(splitter)[1]+subfixer
        xorDiff = int(Decoder.extract("charCodeAt(i))+",");",decodedHtml))
        #logger.info(xorDiff)
        r = ""
        i = 0
        logger.info("starting loop decoder, s: "+s+", k: "+k)
        '''
        r += String.fromCharCode((parseInt(k.charAt(i%k.length))^s.charCodeAt(i))+-2);
        '''
        CORRECTION = 16 #I don't know why but this convert it to legible character (most cases)
        mode = 0
        while i<len(s): #GO TO HELL, REALLY, I HAVE NO IDEA HOW THERE IS PEOPLE IN THE WORLD DOING THIS THING, DO YOU KNOW AN STANDARD ENCODING? YOU DOOOON'T!!!!
            seed = k[(i%len(k))]
            #logger.info("seed: "+seed)
            primitive = ord(seed)^ord(s[i])
            #logger.info("xorted: "+str(primitive))
            if len(r)==0 and str(primitive)!= '<':
                #tryes to check what fix is neccesary
                if str(primitive)=='15':
                    mode = 1
                elif str(primitive)=='14':
                    mode = 2
                elif str(primitive)=='4':
                    mode = 3
                elif str(primitive)=='7':
                    mode = 4
                elif str(primitive)=='9':
                    mode = 5
                else:
                    logger.info("detected new start value: "+str(primitive)+", probably needs new encoding method")
            #mode 1 and mode 2
            if (str(primitive) == '1' and mode==1) or (mode==2 and str(primitive)=='0'):
                r += "."
            elif (str(primitive) == '2' and mode==1) or (mode==2 and (str(primitive)=='1' or str(primitive)=='113')):
                r += "/"
            elif (str(primitive) == '15' and mode==1) or (mode==2 and str(primitive)=='14') or (mode==3 and str(primitive)=='4') or (mode==4 and str(primitive)=='7') or (mode==5 and str(primitive)=='9'):
                r += "<"
            elif (str(primitive) == '112' and mode==1) or (mode==2 and str(primitive)=='15') or (str(primitive) == '5' and mode==3) or (str(primitive) == '8' and mode==4) or (mode==5 and str(primitive)=='10'):
                r += "="
            elif (str(primitive) == '113' and mode==1) or (mode==2 and str(primitive)=='112') or (str(primitive) == '6' and mode==3) or (str(primitive) == '9' and mode==4) or (mode==5 and str(primitive)=='11'):
                r += ">"
            elif (str(primitive) == '13' and mode==1) or (mode==2 and str(primitive)=='12') or (str(primitive) == '2' and mode==3) or (str(primitive) == '5' and mode==4) or (mode==5 and str(primitive)=='7'):
                r += ":"
            elif (int(str(primitive))-3<10 and mode==1):
                r += str(int(str(primitive))-3)
            elif (int(str(primitive))-2<10 and mode==2):
                r += str(int(str(primitive))-2)
            #mode 3
            elif (str(primitive) == '1' and mode==3) or (str(primitive) == '4' and mode==4):
                r += "9"
            elif (str(primitive) == '1' and mode==4) or (str(primitive) == '3' and mode==5):
                r += "6"
            elif (str(primitive) == '110' and mode==3):
                r += "f"
            elif (str(primitive) == '105' and mode==3) or (str(primitive) == '108' and mode==4) or (mode==5 and str(primitive)=='110'):
                r += "a"
            elif (str(primitive) == '109' and mode==3):
                r += "e"
            elif (str(primitive) == '40' and mode==3) or (str(primitive) == '43' and mode==4) or (mode==5 and str(primitive)=='45'):
                r += " "
            elif (str(primitive) == '108' and mode==3):
                r += "d"
            elif (str(primitive) == '42' and mode==3) or (str(primitive) == '45' and mode==4) or (mode==5 and str(primitive)=='47'):
                r += '"'
            elif (str(primitive) == '111' and mode==3):
                r += 'g'
            elif (str(primitive) == '81' and mode==3):
                r += 'i'
            elif (str(primitive) == '107' and mode==3) or (str(primitive) == '110' and mode==4):
                r += 'c'
            elif ((str(primitive) == '10' or str(primitive) == '106') and mode==3) or (str(primitive) == '109' and mode==4) or (mode==5 and str(primitive)=='111'):
                r += 'b'
            #mode 4
            elif mode==4 and str(primitive)=='105':
                r += 'a'
            elif  (str(primitive) == '111' and mode==4):
                r += 'd'
            #mode 5
            elif (mode==5 and str(primitive)=='1'):
                r += '4'
            elif (mode==5 and str(primitive)=='5'):
                r += '8'
            elif (mode==5 and str(primitive)=='108'):
                r += '_'
            elif (mode==5 and str(primitive)=='12'):
                r += '?'
            else:
                integer = primitive+xorDiff
                #logger.info("new value: "+chr(integer+CORRECTION))
                r += chr(integer+CORRECTION)
            #logger.info("r is now: "+r)
            i+=1
        logger.info("loop decoder finished at: "+str(i)+" loop")
        logger.info("final decoded value is: "+r)
        return r


    @staticmethod
    def extractScriptIframeUrl(html,scriptUrl,referer):
        iframeUrl = ""
        scriptContent = Cricfreetv.getContentFromUrl(scriptUrl,"",Cricfreetv.cookie,referer)
        #print scriptContent
        iframeUrl = Decoder.extract('src="','"',scriptContent)
        if iframeUrl.find("id='+id+'")>-1: #search id in html
            id = Decoder.extract("<script type='text/javascript'>id='","';",html)
            iframeUrl = iframeUrl[0:iframeUrl.find('?id=')+len('?id=')]+id+Cricfreetv.getWidthAndHeightParams(html)+"&stretching="
        elif iframeUrl.find("live=")>-1:
            if html.find("<script type='text/javascript'>fid='")>-1:
                id = Decoder.extract("<script type='text/javascript'>fid='","';",html)
            else:
                id = Decoder.extract('<script>fid="','";',html)
            iframeUrl = iframeUrl[0:iframeUrl.find('?live=')+len('?live=')]+id+Cricfreetv.getWidthAndHeightParams(html)
        else:
            iframeUrl = Decoder.extract("<iframe src='","' ",scriptContent)
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