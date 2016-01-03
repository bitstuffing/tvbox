# -*- coding: utf-8 -*-

import httplib
import urllib
import os
import binascii
from core.decoder import Decoder
from core import jsunpack
from core import logger
from core.downloader import Downloader

class Vipracinginfo(Downloader):

    MAIN_URL = "http://vipracing.info"

    @staticmethod
    def getChannels(page):
        x = []
        if str(page) == '0':
            page=Vipracinginfo.MAIN_URL
            html = Vipracinginfo.getContentFromUrl(page,"",Vipracinginfo.cookie,"")
            #print html
            if html.find("var channels = JSON.parse('")>-1: #it's a list, needs decode
                table = Decoder.extract("var channels = JSON.parse('","'),",html)
                table = table.replace('\u00f3','ó').replace('\u00f1','ñ').replace('\/',"-")#.replace('"',"'")
                x = Vipracinginfo.extractElements(table)
                logger.info("Vipracing channels logic done!")
        else:
            html = Vipracinginfo.getContentFromUrl(page,"",Vipracinginfo.cookie,Vipracinginfo.MAIN_URL)
            logger.info("launching Vipracing else logic")
            if html.find('http://www.streamlive.to/embed/')>-1:
                iframeUrl = "http://www.streamlive.to/view/"+Decoder.extract('http://www.streamlive.to/embed/','&width=',html)
                html2 = Vipracinginfo.getContentFromUrl(iframeUrl,"",Vipracinginfo.cookie,page)
                link = "http://harddevelop.blogspot.com/2015/11/tv-box.html" #not a good to force if this link is not updated an error
                if html2.find("http://www.streamlive.to/ads/ilive_player.swf")>-1: #builds the link
                    swfUrl = "http://www.streamlive.to/ads/streamlive.swf"
                    tokenUrl = Decoder.extractWithRegex("http://www.streamlive.to/server.php?id=",'"',html2)
                    tokenUrl = tokenUrl[:(len(tokenUrl)-1)]
                    token = Vipracinginfo.getContentFromUrl(tokenUrl,"",Vipracinginfo.cookie,page)
                    token = Decoder.extract('{"token":"','"}',token)
                    file = Decoder.extract('file: "','",',html2).replace('.flv','')
                    streamer = Decoder.extract('streamer: "','",',html2).replace("\\","")
                    link = streamer+"./"+file+" playpath="+file+" live=1 token="+token+" swfUrl="+swfUrl+" pageUrl=http://www.streamlive.to/view"+(iframeUrl[iframeUrl.rfind("/"):])
                    logger.info("built a link to be used: "+link)
                element = {}
                element["link"] = link
                element["title"] = Decoder.extract("<title>","</title>",html2)
                element["permalink"] = True
                x.append(element)
            elif html.find("http://www.janjua.tv")!=-1:
                channel = Decoder.extract(" width=653, height=410, channel='","'",html)
                url2 = "http://www.janjuaplayer.com/embedplayer/"+channel+"/1/653/410"
                html2 = Vipracinginfo.getContentFromUrl(url2,"",Vipracinginfo.cookie,page)
                bruteContent = Decoder.extract("so.addParam('FlashVars', '","');",html2)
                #extract id and pk
                id = bruteContent[0:bruteContent.find("&")]
                pk = bruteContent[bruteContent.find('pk='):]
                # loadbalancer is http://www.janjuapublisher.com:1935/loadbalancer?53346
                ip = Vipracinginfo.getContentFromUrl("http://www.janjuapublisher.com:1935/loadbalancer?"+(id[id.find("=")+1:]),"","","http://www.janjuaplayer.com/resources/scripts/eplayer.swf").replace('redirect=','')
                link = "rtmp://"+ip+"/live"+" swfUrl=http://www.janjuaplayer.com/resources/scripts/eplayer.swf pageUrl="+url2+" flashver=WIN/2019,0,0,226 live=true timeout=11 playpath="+channel+"?"+id+"&"+pk
                link = "rtmp://"+ip+"/live"+channel+"?"+id+"&"+pk+" app=live pageUrl="+url2+" swfUrl=http://www.janjuaplayer.com/resources/scripts/eplayer.swf tcUrl=rtmp://"+ip+"/live playPath="+channel+"?"+id+"&"+pk+" conn=S:OK live=1 flashver=WIN/2019,0,0,226"
                element = {}
                element["link"] = link
                element["title"] = channel
                element["permalink"] = True
                x.append(element)
            else:
                logger.info("launching Vipracing else ELSE logic (other provider embed - max-deportv)")
                iframeUrl = Decoder.extract(' SRC="','"',html)
                html2 = Vipracinginfo.getContentFromUrl(iframeUrl,"",Vipracinginfo.cookie,page)
                iframeUrl2 = Decoder.extractWithRegex("http://max-deportv",'"',html2)
                iframeUrl2 = iframeUrl2[0:len(iframeUrl2)-1]
                logger.info("using iframeUrl: "+iframeUrl2)
                html3 = Vipracinginfo.getContentFromUrl(iframeUrl2,"",Vipracinginfo.cookie,iframeUrl)
                iframeUrl3 = Decoder.extractWithRegex('http://www.iguide.to/embed/','">',html3)
                iframeUrl3 = iframeUrl3[:len(iframeUrl3)-1]
                #extract channelId
                channelId = Decoder.extract('embed/','&',iframeUrl3)
                iframeUrl3 = "http://www.iguide.to/embedplayer_new.php?width=650&height=400&channel="+channelId+"&autoplay=true"
                html4 = Vipracinginfo.getContentFromUrl(iframeUrl3,"",Vipracinginfo.cookie,iframeUrl2)
                #at this point is a similar logic than streamlive.to (probably because like always it's the same server), builds the link
                swfUrl = Decoder.rExtractWithRegex("http://",".swf",html4)
                logger.info("using swfUrl: "+swfUrl)
                tokenUrl = Decoder.extractWithRegex("http://www.iguide.to/serverfile.php?id=",'"',html4)
                tokenUrl = tokenUrl[:(len(tokenUrl)-1)]
                token = Vipracinginfo.getContentFromUrl(tokenUrl,"",Vipracinginfo.cookie,page)
                token = Decoder.extract('{"token":"','"}',token)
                file = Decoder.extract("'file': '","',",html4).replace('.flv','')
                streamer = Decoder.extract("'streamer': '","',",html4).replace("\\","")
                link = streamer+" playpath="+file+" live=1 token="+token+" swfUrl="+swfUrl+" pageUrl="+iframeUrl3
                logger.info("built a link to be used: "+link)
                element = {}
                element["link"] = link
                element["title"] = Decoder.extract("<title>","</title>",html4)
                element["permalink"] = True
                x.append(element)
        return x

    @staticmethod
    def extractElements(table):
        x = []
        i = 0
        for value in table.split('"name"'):
            if i>0:
                element = {}
                title = Decoder.extract('"','"',value).replace('- ','')
                link = Decoder.extract('shortcut":"','"',value)
                element["title"] = title
                element["link"] = "http://vipracing.info/channel/"+link+"/frame"
                logger.info("append: "+title+", link: "+element["link"])
                x.append(element)
            i+=1
        return x