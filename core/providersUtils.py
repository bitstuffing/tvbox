# -*- coding: utf-8 -*-
import urllib
import sys

from core.xbmcutils import XBMCUtils
from core.addonUtils import add_dir
from core.addonUtils import open
from core import logger
from core.decoder import Decoder
from core.downloader import Downloader

from core.listsParsers import getListsUrls

from providers.filmoncom import Filmoncom
from providers.hdfulltv import HdfullTv
from providers.vigoalnet import Vigoal
from providers.cinestrenostv import Cineestrenostv
from providers.cricfreetv import Cricfreetv
from providers.zoptvcom import Zoptvcom
from providers.live9net import Live9net
from providers.sports4u import Sports4u
from providers.vipracinginfo import Vipracinginfo
from providers.hdfullhdeu import Hdfullhdeu
from providers.skylinewebcamscom import Skylinewebcamscom
from providers.zonasportsme import Zonasportsme
from providers.sportstream365com import Sportstream365com
from providers.showsporttvcom import ShowsportTvCom
from providers.mamahdcom import Mamahdcom
from providers.arenavisionin import Arenavisionin
from providers.acetvru import Acetvru
from providers.youtube import Youtube
from providers.zonaappcom import ZonaAppCom
from providers.pastebin import Pastebin
from providers.redeneobuxcom import RedeneobuxCom
from providers.tunein import TuneIn
from providers.reuters import Reuters
from providers.youtvgratiscom import Youtvgratis
from providers.yomvies import Yomvies

try:
	from providers.spliveappcom import Spliveappcom
except:
	logger.error("Crypto-problems detected, probably you need a better platform")
	pass

from window.DefaultWindow import DefaultWindow

icon = XBMCUtils.getAddonFilePath('icon.png')

def drawFilmon(page):
	jsonChannels = Filmoncom.getChannelsJSON()
	for itemFirst in jsonChannels:
		if page == "0":
			add_dir(itemFirst["title"],"http://www.filmon.com/tv/"+itemFirst["alias"],4,icon,"filmoncom",itemFirst["title"])
		elif (page == itemFirst["title"]) and itemFirst.has_key("channels") :
			for item in itemFirst["channels"]:
				add_dir(item["title"],"http://www.filmon.com/tv/"+item["alias"],5,item["logo"],"filmoncom",item["title"])
		else:
			logger.info("no channel: "+page)

def drawHdfulltv(page):
	mode = 4 #continue browsing
	jsonChannels = HdfullTv.getChannels(page)
	for itemFirst in jsonChannels:
		if itemFirst.has_key("permalink"):
			if itemFirst.has_key("show"): #serie
				link = "http://hdfull.tv/serie/"+itemFirst["permalink"]+"/temporada-"+itemFirst["season"]+"/episodio-"+itemFirst["episode"]
				title = itemFirst["show"]["title"]
				if type(title) == type(dict()):
					if title.has_key("es"):
						title = title["es"]
					else:
						title = ""
					if len(title)==0 and itemFirst["title"].has_key("en"):
						title = itemFirst["title"]["en"]
				#put the season and the chapter
				chapter = int(itemFirst["episode"])
				if chapter<10:
					chapterString = "0"+str(chapter)
				else:
					chapterString = str(chapter)
				title = title+" "+itemFirst["season"]+"x"+chapterString
			else:
				if(itemFirst["permalink"].find("http://")>-1):
					link = itemFirst["permalink"]
				elif itemFirst["permalink"].find("http")>-1:
					link = itemFirst["permalink"]
				else:
					link = "http://hdfull.tv/"+itemFirst["permalink"]
				title = itemFirst["title"]
				if type(title) == type(dict()):
					if title.has_key("es"):
						title = title["es"]
					else:
						title = ""
					if len(title)==0 and itemFirst["title"].has_key("en"):
						title = itemFirst["title"]["en"]
			if itemFirst.has_key("thumbnail"):
				image = itemFirst["thumbnail"]
				if image.find("http://")<0:
					image = "http://hdfull.tv/tthumb/130x190/"+image
			else:
				image = icon
		if itemFirst.has_key("finalLink"):
			mode = 100 #open link from provider
		add_dir(title,link,mode,image,"hdfulltv",link)

def drawVipgoal(page):
	jsonChannels = Vigoal.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		if title=='Display by event':
			title = XBMCUtils.getString(10006)
		link = item["link"]
		if link != '1':
			mode = 101 #next step returns a final link
		else:
			mode = 4 #continue browsing
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
		else:
			image = icon
		add_dir(title,link,mode,image,"vigoal",link)

def drawCinestrenostv(page):
	jsonChannels = Cineestrenostv.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		mode = 102 #next step returns a final link
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
		else:
			image = icon
		add_dir(title,link,mode,image,"cineestrenos",link)

def drawCricfree(page):
	jsonChannels = Cricfreetv.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		if title=='Display by event':
			title = XBMCUtils.getString(10006)
		link = item["link"]
		if link=='1':
			mode = 4
		else:
			mode = 103 #next step returns a final link
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
		else:
			image = icon
		add_dir(title,link,mode,image,"cricfree",link)

def drawZoptv(page):
	jsonChannels = Zoptvcom.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		if title=='Browse by Country':
			title = XBMCUtils.getString(10007)
		elif title=='Browse by Genre':
			title = XBMCUtils.getString(10008)
		link = item["link"]
		mode = 4
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			mode = 104
		else:
			image = icon
		add_dir(title,link,mode,image,"zoptv",link)

def drawLive9(page):
	jsonChannels = Live9net.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		mode = 105 #next step returns a final link
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
		else:
			image = icon
		add_dir(title,link,mode,image,"live9",link)

def drawSports4u(page):
	jsonChannels = Sports4u.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		mode = 106 #next step returns a final link
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
		else:
			image = icon
		add_dir(title,link,mode,image,"sports4u",link)

def drawVipracinginfo(page):
	jsonChannels = Vipracinginfo.getChannels(page)
	mode = 107
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		add_dir(title,link,mode,icon,"vipracinginfo",link)

def drawHdfullhdeu(page):
	jsonChannels = Hdfullhdeu.getChannels(page)
	mode = 4
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		if item.has_key("permaLink"):
			mode = 2
		add_dir(title,link,mode,icon,"hdfullhdeu",link)

def drawSkylinewebcams(page):
	jsonChannels = Skylinewebcamscom.getChannels(page)
	mode = 4
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: "+image)
		else:
			image = icon
		if item.has_key("permaLink"):
			mode = 108
		add_dir(title,link,mode,image,"skylinewebcams",link)

def drawZonasportsme(page):
	mode = 109
	jsonChannels = Zonasportsme.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		image = icon
		add_dir(title,link,mode,image,"zonasportsme",link)

def drawSportstream365(page):
	mode = 110
	jsonChannels = Sportstream365com.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		image = icon
		add_dir(title,link,mode,image,"sportstream365com",link)

def drawSplive(page):
	mode = 4
	jsonChannels = Spliveappcom.getChannels(page)
	image = icon
	for item in jsonChannels:
		try:
			logger.debug("trying splive item...")
			#title = urllib.unquote_plus(item["title"].decode('iso-8859-1', 'ignore'))
			title = item["title"]
			link = item["link"]
			referer = "splive"
			if item.has_key("permaLink"):
				mode = 111
				if item.has_key("referer"):
					referer = item["referer"]
					logger.info("referer is: "+referer)
			if item.has_key("thumbnail"):
				image = item["thumbnail"]
				logger.info("detected img: "+image)
			else:
				image = icon
			add_dir(title,link,mode,image,referer,link)
		except:
			logger.error("Something goes wrong with SPLIVEAPP drawer")
			pass

def drawMamahdcom(page):
	mode = 4
	jsonChannels = Mamahdcom.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		if item.has_key("permaLink"):
			mode = 112
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: "+image)
		else:
			image = icon
		add_dir(title,link,mode,image,"mamahdcom",link)

def drawShowsporttvcom(page):
	mode = 4
	jsonChannels = ShowsportTvCom.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		if title=='Display by event':
			title = XBMCUtils.getString(10006)
		link = item["link"]
		if link!='1':
			mode = 113
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: "+image)
		else:
			image = icon
		add_dir(title,link,mode,image,"showsporttvcom",link)

def drawArenavisionin(page):
	mode = 4
	jsonChannels = Arenavisionin.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		if title=='Display by event':
			title = XBMCUtils.getString(10006)
		link = item["link"]
		if link!='1':
			mode = 114
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: "+image)
		else:
			image = icon
		add_dir(title,link,mode,image,"arenavisionin",link)

def drawAcetvru(page):
	mode = 2
	jsonChannels = Acetvru.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		if title=='Display by event':
			title = XBMCUtils.getString(10006)
		link = item["link"]
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: "+image)
		else:
			image = icon
		add_dir(title,link,mode,image,"acetvru",link)

def drawYoutube(url='0'): #BROWSES ALL PROVIDERS (it has been re-sorted)
	#static content
	channels = Youtube.getChannels(url)
	logger.debug("items obtained: "+str(len(channels)))
	for channel in channels:
		image = ''
		level = 4
		if channel.has_key('finalLink'):
			level = 115
		if channel.has_key('thumbnail'):
			image = channel["thumbnail"]
		add_dir(channel["title"], channel["page"], level, image, "youtube", channel["page"])

def drawZonaAppCom():
	channels = ZonaAppCom.getChannelsJSON()
	logger.debug("items obtained: " + str(len(channels)))
	for channel in channels:
		image = ''
		level = 116
		if channel.has_key('thumbnail'):
			image = channel["thumbnail"]
		add_dir(channel["title"], channel["link"], level, image, "zonaappcom", channel["link"])

def drawPastebinCom():
	param = urllib.quote_plus(str(XBMCUtils.getSettingFromContext(sys.argv[1],'pastebin_param')))
	logger.debug("extracted param to be searched: "+param)
	channels = Pastebin.searchLists(param=param)
	logger.debug("items obtained: " + str(len(channels)))
	level = 1
	for channel in channels:
		add_dir(channel["title"], channel["link"], level, '', "pastebincom", channel["link"])

def drawRedeneobuxCom(url):
	channels = RedeneobuxCom.getChannels(url)
	logger.debug("items obtained: " + str(len(channels)))
	for channel in channels:
		level = 4
		if channel.has_key("finalLink"):
			level = 2 #m3u8 list
		img = ''
		if channel.has_key("thumbnail"):
			img = channel["thumbnail"]
		add_dir(channel["title"], channel["link"], level, img, "redeneobuxcom", channel["link"])

def drawTuneIn(url):
	channels = TuneIn.getChannels(url)
	logger.debug("items obtained: " + str(len(channels)))
	for channel in channels:
		level = 4
		if channel.has_key("finalLink"):
			level = 118  # stream
		img = ''
		if channel.has_key("thumbnail"):
			img = channel["thumbnail"]
		add_dir(channel["title"], channel["link"], level, img, "tunein", channel["link"])

def drawYoutvgratis(url):
	channels = Youtvgratis.getChannels(url)
	logger.debug("items obtained: " + str(len(channels)))
	level = 119  # stream
	for channel in channels:
		img = ''
		if channel.has_key("thumbnail"):
			img = channel["thumbnail"]
		add_dir(channel["title"], channel["link"], level, img, "youtvgratis", channel["link"])

def drawYomviEs(page):
	mode = 120
	jsonChannels = Yomvies.getChannels(page)
	for item in jsonChannels:
		title = item["title"]
		link = item["link"]
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: " + image)
		else:
			image = icon
		add_dir(title, link, mode, image, "yomvies", link)

def drawNews(url,provider='',targetAction=1): #from rss page
	if targetAction==4 and provider=="bbccouk" and ".xml" not in url:
		drawBbcCoUkNew(url)
	else:
		getListsUrls(url,provider=provider,finalTarget=targetAction)

def drawReutersNews(url): #from rss page
	x = Reuters.getChannels(url)
	if str(url)=='0':
		level = 4
		for new in x:
			img = ''
			if new.has_key("thumbnail"):
				img = new["thumbnail"]
			add_dir(new["title"], new["link"], level, img, "reuters", 1)
	else:
		body = x[0]["title"]
		drawNew(textContent=(body))

def drawBbcCoUkNew(url):
	htmlContent = Downloader.getContentFromUrl(url=url)
	title = Decoder.extract('<p class="story-body__introduction">','</p><div',htmlContent)
	if 'property="articleBody"' in htmlContent:
		body = Decoder.extract('property="articleBody"','                                                                                                </div>',htmlContent)
		body = body.replace('<span class="off-screen">Image copyright</span>','')
		body = body.replace('<span class="story-image-copyright">AFP</span>', '')
		body = body.replace('<span class="story-image-copyright">Reuters</span>', '')
		body = body.replace('<span class="off-screen">Image caption</span>', '')
		body = body.replace('<span class="off-screen">Media caption</span>','')
		while '<span class="media-caption__text">' in body:
			line = Decoder.extractWithRegex('<span class="media-caption__text">',"</span>",body)
			body = body.replace(line,"")
	elif 'class="text-wrapper"' in htmlContent:
		#special content
		body = Decoder.extract('class="text-wrapper"','</p>\n',htmlContent)
		dates = Decoder.extractWithRegex('<div class="date',"</div>",body)
		lastUpdate = Decoder.extractWithRegex('<p class="date ', "</p>", body)
		body = body.replace(dates,"")
		body = body.replace(lastUpdate, "")
	elif '<figcaption class="sp-media-asset' in htmlContent:
		body = Decoder.extract('<figcaption class="sp-media-asset', '</p><div ', htmlContent)
		if '>' in body:
			body = body[body.find(">") + 1:]
	body = Decoder.removeHTML(body).replace(".", ".\n").replace(">", "")
	logger.debug("body is: " + body)
	drawNew(textContent=(body))

def drawNew(textContent,img=''):
	TypeOfMessage = "t" #text
	NewMessage = textContent
	TempWindow = DefaultWindow(noteType=TypeOfMessage, noteMessage=NewMessage, logo=img)
	TempWindow.doModal()
	del TempWindow

def drawFilmonLinks(url, page, provider=""):
	finalUrls = Filmoncom.getChannelUrl(url)
	for finalUrl in finalUrls:
		add_dir(page+", "+finalUrl["name"],finalUrl["url"],2,provider,page)
		#print("page: "+page+", url: "+finalUrl["url"])

def decodeAndOpenLink(url,page):
    logger.info("decoding: " + url)
    link = Decoder.decodeLink(url)
    logger.info("decoded: " + link)
    open(link, page)

def openVipgoalLink(url,page):
    jsonChannels = Vigoal.getChannels(page)
    url = jsonChannels[0]["link"]
    logger.info("found link: " + url + ", launching...")
    open(url, page)  # same that 2, but reserved for rtmp

def openCineestrenosLink(url,page):
    jsonChannels = Cineestrenostv.getChannels(page)
    url = jsonChannels[0]["link"]
    logger.info("found link: " + url + ", launching...")
    open(url, page)

def openCricFreeLink(url,page):
    channel = Cricfreetv.getChannels(page)
    logger.info("found link: " + channel[0]["link"] + ", launching...")
    open(channel[0]["link"], page)

def openZopTvLink(url,page):
	channel = Zoptvcom.getChannels(page)
	logger.info("found link: " + channel[0]["link"] + ", launching...")
	open(channel[0]["link"], page)

def openLive9Link(url,page):
	channel = Live9net.getChannels(page)
	logger.info("found link: " + channel[0]["link"] + ", launching...")
	open(channel[0]["link"], page)

def openSports4uLink(url,page):
	channel = Sports4u.getChannels(page)
	logger.info("found link: " + channel[0]["link"] + ", launching...")
	open(channel[0]["link"], page)

def openVipracingLink(url,page):
	channel = Vipracinginfo.getChannels(page)
	logger.info("found link: " + channel[0]["link"] + ", launching...")
	open(channel[0]["link"], page)

def openSkylineLink(url,page):
	channel = Skylinewebcamscom.getChannels(page, True)
	logger.info("found link: " + channel[0]["link"] + ", launching...")
	open(channel[0]["link"], page)

def openZonasportsLink(url,page):
	channel = Zonasportsme.getChannels(url)
	logger.info("found link: " + channel[0]["link"] + ", launching...")
	open(channel[0]["link"], page)

def openSports365Link(url,page):
	channel = Sportstream365com.getChannels(url)
	logger.info("found link: " + channel[0]["link"] + ", launching...")
	open(channel[0]["link"], page)

def openSpliveLink(url,page,provider):
	if url.find(".m3u8") == -1 and url.find("rtmp://") == -1:
		channel = Spliveappcom.decodeUrl(url, provider)
		link = channel[0]["link"]
		if link.find(", referer:") > -1:
			link = link[0:link.find(", referer:")]
		url = link
	else:
		logger.debug("nothing decoded for splive encrypted channels, continue...")

	logger.debug("splive BRUTE logic for url: " + url)

	try:
		if 'ponlatv.com' in url or 'playerhd1.pw' in url:
			logger.debug("trying to decode cineestrenos script from url: " + url)
			url = Cineestrenostv.extractScriptLevel3(url,referer=Cineestrenostv.MAIN_URL)
			logger.debug("decoded link was: "+url)

		else:
			url = Cineestrenostv.getChannels(url)[0]["link"]
			html = Downloader.getContentFromUrl(url)
			element = Cineestrenostv.extractIframeChannel(html, url)
			if element is not None and element.has_key("link"):
				url = element["link"]
				logger.debug("cineestrenos url was decoded to: " + url)
			else:
				logger.debug("nothing was done to decode cineestrenostv url!")
	except:
		logger.debug("nothing to be decoded with url: " + url)
		pass

	link = url

	logger.info("found link: " + link + ", launching...")
	open(link, page)

def openMamahdLink(url,page):
	channel = Mamahdcom.getChannels(url)
	logger.info("found link: " + channel[0]["link"] + ", launching...")
	open(channel[0]["link"], page)

def openShowsportsLink(url,page):
	channel = ShowsportTvCom.getChannels(url)
	logger.info("found link: " + channel[0]["link"] + ", launching...")
	open(channel[0]["link"], page)

def openArenavisionLink(url,page):
	channel = Arenavisionin.getChannels(url)
	logger.info("found link: " + channel[0]["link"] + ", launching...")
	open(channel[0]["link"], page)

def openYoutubeLink(url,page): #could be replaced by decodeAndOpenLink, traces are the unique difference
	logger.info("decoding youtube link... " + url)
	link = Decoder.decodeLink(url)
	logger.info("decoded youtube link: " + link)
	open(link, page)

def openZonaappLink(url,page):
	logger.info("decoding zonaapp link... " + url)
	link = ZonaAppCom.getFinalLink(url)
	logger.info("decoded zonaapp link: " + link)
	open(link, page)

def openTuneInLink(url,page):
	logger.info("decoding tunein link... " + url)
	link = TuneIn.getChannels(url)[0]["link"]
	logger.info("decoded tunein link: " + link)
	open(link, page)

def openYoutvgratisLink(url,page):
	logger.info("decoding youtvgratis link... " + url)
	link = Youtvgratis.getChannels(url)[0]["link"]
	logger.info("decoded youtvgratis link: " + link)
	open(link, page)

def openYomvies(url,page):
	logger.info("decoding yomvi link... " + url)
	link = Yomvies.getChannels(url)[0]["link"]
	logger.info("decoded yomvi link: " + link)
	open(link, page)

def isAnException(url,page,provider,mode):
	state = False
	if mode == 4 and (provider=="bbccouk" and str(page) == '0' and ".xml" not in url) or (str(page)=='1' and provider=='reuters'):
		state = True
	if state:
		logger.debug("Dont reload view. Params -> page: "+page+", url: "+url+", provider: "+provider+", mode: "+str(mode))
	return state




