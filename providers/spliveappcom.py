# -*- coding: utf-8 -*-

import httplib
import urllib
import binascii
import sys
import xbmcplugin

from core.decoder import Decoder
from core import jsunpack
from core import logger
from core.downloader import Downloader
from core.cipher import PBEWithMD5AndDES

class Spliveappcom(Downloader):

    MAIN_URL = xbmcplugin.getSetting(int(sys.argv[1]), "splive_channel")

    PASSWORD = 'c6ka74t4b2dv'

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == '0':
            page=Spliveappcom.MAIN_URL
            if page.find("pastebin.com/")>-1 and page.find("/raw/")==-1:
                page = page.replace(".com/",".com/raw/")
        html = Spliveappcom.getContentFromUrl(page,"",Spliveappcom.cookie,"")
        x = Spliveappcom.extractElements(html)
        return x

    @staticmethod
    def extractElements(table):
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
            if img.find("http")==-1:
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
            decrypted = PBEWithMD5AndDES.decrypt(encrypted, Spliveappcom.PASSWORD)
            logger.debug("Decrypted content is: "+decrypted)
        except:
            logger.error("Could not be unencrypted: "+encrypted)
            pass

        return decrypted


