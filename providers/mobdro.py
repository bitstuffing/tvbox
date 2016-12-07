# -*- coding: utf-8 -*-
from core.decoder import Decoder
from core import logger
from core.downloader import Downloader
from core.xbmcutils import XBMCUtils

try:
    import json
except:
    import simplejson as json

import urllib,urllib2,sys,time,md5,base64

class Mobdro(Downloader):

    MAIN_URL = "mobdro.me"
    CHANNELS = "channels"
    API_URL = "https://api.mobdro.sx/streambot/v4/show"
    TOKEN = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "mobdro_api")  #stored for premium support, implementation will change

    @staticmethod
    def getChannels(page):
        x = []
        logger.debug("using Mobdro...")
        if str(page) == '0': #channels
            response = Mobdro.channel_list(Mobdro.CHANNELS)
            #parse results
            results = json.loads(response)
            for result in results:
                url = parse_relayer(result)
                if url is not "exception":
                    element = {}
                    element["link"] = url
                    element["thumbnail"] = result["img"]
                    element["title"] = result["name"]+ " - "+result["language"]
                    logger.debug("appending: "+element["title"]+", url: "+url)
                    x.append(element)
        return x

    @staticmethod
    def channel_list(action):
        response = "ERROR"
        # On first page, pagination parameters are fixed
        if action is not None:
            c_headers = {"User-Agent": "Mobdro/5.0", "Referer": "api.mobdro.sx"}
            c_data = {'data': action, 'parental': 0, 'languages': '[]', 'alphabetical': 0, 'token': Mobdro.TOKEN}
            c_data = urllib.urlencode(c_data)
            # Fetch channel list
            req = urllib2.Request(Mobdro.API_URL, c_data, c_headers)
            response = urllib2.urlopen(req)
            response = response.read()
        return response

def parse_relayer(params):
    url = "NonE"
    try:
        if params.has_key("url"):
            url = params["url"]
            logger.debug("mobdro.directURL: " + url)
        elif params.has_key("relayer"):
            params2 = json.loads(params["relayer"])
            logger.debug("RELAYED: "+repr(params2))
            protocol = "http"#params2["protocol"]
            app = params2["app"]
            server = params2["server"]
            playpath = params2["playpath"]
            password = params2["password"]
            dire = params2["dir"]
            expiration_time = params2["expiration_time"]
            millis = int(round(time.time() * 1000))
            l = millis / 1000L + expiration_time
            arr = [password, l, dire, playpath]
            url = "%s%d/%s/%s"
            url = url % tuple(arr)
            url_md5 = md5.new(url).digest()
            url_base64 = base64.b64encode(url_md5)
            url_base64 = url_base64.replace("+", "-").replace("/", "_").replace("=", "")
            #arr = [server, url_base64, l, playpath]
            arr = [protocol,server,app,playpath,url_base64,l]
            url = "%s://%s/%s/%s?st=%s&e=%d" #"http://%s/live/%s/%d/%s"
            url = url % tuple(arr)
            url += "|Referer="+Mobdro.MAIN_URL+"&User-Agent=Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.100 Safari/537.36&Icy-MetaData=0"
        else:
            logger.debug("REJECTED: " + repr(params))
    except KeyError:
        url = "exception"
        pass
    return url