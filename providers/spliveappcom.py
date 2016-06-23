# -*- coding: utf-8 -*-
import sys
try:
    import json
except:
    import simplejson as json

import urllib
from core.xbmcutils import XBMCUtils
from core.decoder import Decoder
from core import jsunpack
from core import logger
from core.downloader import Downloader

ONLINE = False
try:
    from core.cipher import PBEWithMD5AndDES
except:
    logger.error("Detected missing pycrypt")
    logger.info("using online decrypter solution...")
    ONLINE = True
    pass

class Spliveappcom(Downloader):

    MAIN_URL = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "splive_channel")
    DECODER_URL = XBMCUtils.getSettingFromContext(int(sys.argv[1]), "online_pbewithmd5anddes_decoder")

    PASSWORD = 'c6ka74t4b2dv'

    @staticmethod
    def getChannels(page,decode=False,group=''):
        x = []
        if str(page) == '0':
            page=Spliveappcom.MAIN_URL
            if page.find("pastebin.com/")>-1 and page.find("/raw/")==-1:
                page = page.replace(".com/",".com/raw/")
        html = Spliveappcom.getContentFromUrl(page,"",Spliveappcom.cookie,"")
        try:
            x = Spliveappcom.extractElements(html,decode)
        except:
            logger.debug("trying json way...")
            x = Spliveappcom.extractJSONElements(html,grouped=group,url=page)
            logger.debug("finished json way...")
            pass
        return x

    @staticmethod
    def extractJSONElements(html,grouped='',url=''):
        x = []
        jsonGlobal = json.loads(html)
        logger.debug("charged json...")
        groups = jsonGlobal["groups"]
        logger.debug("get groups: "+str(len(groups)))
        for group in groups:
            element = {}
            element["title"] = urllib.quote_plus(group["name"].encode('ascii', 'ignore').encode('iso-8859-1', 'ignore'))
            element["thumbnail"] = group["image"]
            element["link"] = url
            if group.has_key("url"):
                logger.debug("extracted station...")
                element["link"] = group["url"]
                element["permaLink"] = True
            elif group.has_key("stations"):
                if grouped is '':
                    element["link"] = group["name"]
                elif group["name"] == grouped:
                    logger.debug("searching for group: "+grouped)
                    for elementLink in group["stations"]:
                        if not elementLink.has_key("isAd"):
                            element = {}
                            element["title"] = elementLink["name"].encode('ascii', 'ignore')
                            element["thumbnail"] = elementLink["image"]
                            element["link"] = elementLink["url"]
                            if len(element["link"])>0:
                                logger.debug("appended grouped: " + element["title"])
                                element["permaLink"] = True
                                x.append(element)

                logger.debug("group station... "+group["name"])
            if element.has_key("link") and grouped is '':
                logger.debug("appended: " + element["title"])
                x.append(element)
        return x


    @staticmethod
    def extractElements(table,decode=False):
        x = []
        i = 0
        permaLink = False
        if table.find("@ /lista")>-1:
            splitter = "@ /lista"
        elif table.find("@ /channel")>-1:
            splitter = "@ /channel"
            permaLink = True
        elif table.find("@ /movie")>-1:
            splitter = "@ /movie"
            permaLink = True
        for value in table.split(splitter):
            element = {}
            title = ""
            link = ""
            referer = ""
            if value.find(" title ")>-1:
                title = Decoder.extract(" title \"","\"",value)
            elif value.find(" name")>-1:
                title = Decoder.extract(" name \"","\"",value)
            if value.find(" url \"")>-1:
                link = Decoder.extract(" url \"","\"",value)
            elif value.find(" url_servidor \"")>-1:
                link = Decoder.extract(" url_servidor \"","\"",value)
            element["title"] = title
            img = ""
            if value.find(" image \"")>-1:
                img = Decoder.extract(" image \"","\"",value)
            elif value.find(" image_url ")>-1:
                img = Decoder.extract(" image_url \"","\"",value)
            if decode and img.find("http")==-1:
                try:
                    img = Spliveappcom.decrypt(img)
                    element["thumbnail"] = img
                except:
                    logger.error("Could not be decoded img content.")
                    pass
            elif img!="":
                element["thumbnail"] = img
            if link.find("pastebin.com"):
                link = link.replace(".com/",".com/raw/")
            element["link"] = link
            if value.find("referer \"")>-1:
                referer = Decoder.extract("referer \"","\"",value)
                if referer!="0":
                    element["referer"] = referer
            if permaLink:
                element["permaLink"] = True
            logger.debug("append: "+title+", link: "+element["link"])
            if title!='' and link!='':
                x.append(element)
            i+=1
        return x

    @staticmethod
    def decodeUrl(url,referer=''):
        #content = Spliveappcom.getContentFromUrl(url)
        if url.find("http")==-1 and (url.find("sop://")==-1 and url.find("acestream://")==-1):
            decryptedUrl = Spliveappcom.decrypt(url)
        else:
            decryptedUrl = url
        element = {}
        element["title"] = "Link"
        if referer!='':
            referer = Spliveappcom.decrypt(referer)
            if referer!='0':
                decryptedUrl+=", referer: "+referer
        logger.debug("brute link to be launched: "+decryptedUrl)
        element["link"] = decryptedUrl
        x = []
        x.append(element)
        return x


    @staticmethod
    def decrypt(encrypted):
        decrypted = encrypted
        try:
            logger.debug("Encrypted content is: "+encrypted)
            if not ONLINE:
                decrypted = PBEWithMD5AndDES.decrypt(encrypted, Spliveappcom.PASSWORD)
            elif len(encrypted)>0 and encrypted.find("http://")==-1:
                decrypted = Downloader.getContentFromUrl(Spliveappcom.DECODER_URL+'?data='+encrypted+"&key="+Spliveappcom.PASSWORD+"&iterations=1000")
            logger.debug("Decrypted content is: "+decrypted)
        except:
            logger.error("Could not be unencrypted: "+encrypted)
            pass

        return decrypted


