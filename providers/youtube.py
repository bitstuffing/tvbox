from core import logger
from core.decoder import Decoder
from core.downloader import Downloader
from core.xbmcutils import XBMCUtils
import urllib

try:
    import json
except:
    import simplejson as json

class Youtube(Downloader):

    MAIN_URL = "https://www.youtube.com"
    SEARCH_URL = "https://www.youtube.com/results?search_query="

    @staticmethod
    def getChannels(page='0'):
        x = []
        if str(page) == '0':
            page=Youtube.MAIN_URL+"/"
            html = Youtube.getContentFromUrl(page,"",Youtube.cookie,"")
            logger.debug("html: "+html)
            x = Youtube.extractMainChannels(html)
            element = {}
            element["title"] = XBMCUtils.getString(11018)
            element["page"] = 'search'
            x.append(element)
        elif str(page) == 'search':
            keyboard = XBMCUtils.getKeyboard()
            keyboard.doModal()
            text = ""
            if (keyboard.isConfirmed()):
                text = keyboard.getText()
                text = urllib.quote_plus(text)
                html = Youtube.getContentFromUrl(Youtube.SEARCH_URL+text, "", Youtube.cookie, "https://www.youtube.com/?app=desktop")
                html = html.replace('\u003e','>').replace("\u003c","<").replace("\\","")
                logger.debug("brute html is: "+html)
                x = Youtube.extractAllVideosFromHtml(html)
                logger.debug("done search logic!")
        elif '/results?' in page:
            logger.debug("pagination detected: "+page)
            html = Youtube.getContentFromUrl(page, "", Youtube.cookie,Youtube.MAIN_URL)
            x = Youtube.extractAllVideosFromHtml(html)
            logger.debug("done search logic pagination!")
        elif page.find('/channel/')>-1:
            html = Youtube.getContentFromUrl(page,"",Youtube.cookie,Youtube.MAIN_URL)
            x = Youtube.extractAllVideos(html)
        elif "/trending" in page:
            html = Youtube.getContentFromUrl(page, "", Youtube.cookie, Youtube.MAIN_URL)
            x = Youtube.extractAllVideosFromHtml(html)
        else:
            link = Youtube.extractTargetVideo(page)
            element = {}
            element["title"] = page
            element["link"] = link
            element["finalLink"] = True
            x.append(element)
        return x

    @staticmethod
    def decodeKeepVid(link):
        html = Downloader.getContentFromUrl("http://keepvid.com/?url="+urllib.quote_plus(link))
        tableHtml = Decoder.extract('<ul><li>',"</ul>",html)
        logger.debug("extracting from html: "+tableHtml)
        links = []
        selectedLink = ""
        for liHtml in tableHtml.split('</li>'):
            link = Decoder.extract('a href="','"',liHtml)
            title = Decoder.extract('alt="', '"', liHtml)
            if "1080p" in title and '(Video Only)' not in title:
                selectedLink = link
            elif len(selectedLink)==0 and "720p" in title and '(Video Only)' not in title:
                selectedLink = link
            else:
                logger.debug("No link selected with title: "+title)
            logger.debug("url at this moment is (youtube external): " + link)
            links.append(link)
        if len(selectedLink)==0:
            selectedLink = links[0]
        return selectedLink

    @staticmethod
    def extractTargetVideo(link):
        logger.debug("trying to decode with youtube link decrypter: " + link)
        code = link[link.find("v=") + 2:]
        logger.debug("trying with code: " + code)
        try:
            link = Decoder.downloadY(code)
        except:
            # trying second way, external page

            html = Downloader.getContentFromUrl(link, referer=Youtube.MAIN_URL)
            oldLink = link
            if 'ytplayer.config = {' in html:
                logger.debug("trying new way for .m3u8 links...")
                link = Decoder.extract(',"hlsvp":"', '"', html).replace('\\', '')
                logger.debug("new youtube extracted link from json is: " + link)
                link = urllib.unquote(link)
                # link += "|" + Downloader.getHeaders(oldLink)
            if "http" not in link:
                logger.debug("trying old second way: external resource...")
                link = Youtube.decodeKeepVid(oldLink)
            pass
        logger.debug("final youtube decoded url is: " + link)
        return link


    @staticmethod
    def extractAllVideosFromHtml(html):
        x = []
        tableHtml = Decoder.extract('class="item-section">','</ol>',html)
        i=0
        for rowHtml in tableHtml.split('<div class="yt-lockup-dismissable yt-uix-tile">'):
            if i>0:
                element = {}
                link = Decoder.extract(' href="', '"', rowHtml)
                title = Decoder.rExtract('title="','" aria-describedby="', rowHtml).replace('" rel="spf-prefetch','')
                logger.debug("link: "+link+", title is: "+title)
                if 'youtube.com' not in link:
                    link = Youtube.MAIN_URL+link
                image = Decoder.extractWithRegex('https://i.ytimg.com/','"',rowHtml).replace('"','')
                element["title"] = title
                element["page"] = link
                element["finalLink"] = True
                element["thumbnail"] = image
                x.append(element)
            i+=1
        #add next if pagination exists
        if '<div class="branded-page-box search-pager  spf-link ">' in html:
            bruteHtmlPaginate = Decoder.rExtract('<div class="branded-page-box search-pager  spf-link ">','<div class="branded-page-v2-secondary-col">',html)
            title = Decoder.rExtract(">","</span></a>",bruteHtmlPaginate)
            title = title[:len(title)-2]
            link = Decoder.rExtract('href="','" class="yt-uix-button', bruteHtmlPaginate)
            if 'youtube.com' not in link:
                link = Youtube.MAIN_URL + link
            element = {}
            element["title"] = title
            element["page"] = link
            logger.debug("link: " + link + ", title is: " + title)
            x.append(element)
        return x

    @staticmethod
    def extractAllVideos(html):
        x = []
        jsonScript = Decoder.extract('<script type="application/ld+json">','</script>',html).strip()
        #logger.debug("json: "+jsonScript)
        jsonList = json.loads(jsonScript)
        for element in jsonList['itemListElement']:
            #logger.debug("element: "+str(element))
            if element.has_key('item'):
                for element2 in element["item"]["itemListElement"]:
                    #logger.debug("element2: "+str(element2))
                    target = {}
                    target["page"] = str(element2["url"])
                    code = target["page"][target["page"].rfind("=")+1:]
                    target["thumbnail"] = "https://i.ytimg.com/vi/"+code+"/mqdefault.jpg"
                    target["title"] = Decoder.extract('href="/watch?v='+code+'">',"</",html)
                    logger.debug("appended: "+target["title"]+", url: "+target["page"])
                    target["finalLink"] = True
                    x.append(target)
        return x

    @staticmethod
    def extractMainChannels(html):
        x = []
        i = 0
        for value in html.split('guide-item yt-uix-sessionlink yt-valign spf-link'):
            if i>0 and value.find("href=\"")>-1 and value.find('title="')>-1:
                element = {}
                title = Decoder.extract('title="','"',value)
                link = Youtube.MAIN_URL+Decoder.extract('href="','"',value)
                element["title"] = title
                element["page"] = link
                if value.find('<img src="')>-1:
                    element["thumbnail"] = Decoder.extract('<img src="','"',value)
                    logger.debug("thumbnail: "+element["thumbnail"])
                logger.debug("append: "+title+", link: "+element["page"])
                if "Home" not in title and "Movies" not in title:
                    x.append(element)
            i+=1
        return x