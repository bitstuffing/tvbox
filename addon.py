# -*- coding: utf-8 -*-

import CommonFunctions as common
import urllib
import urllib2
import os,sys
import xbmcplugin
import xbmcgui
import xbmcaddon
from core import updater
from core import logger
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
from core.decoder import Decoder
import re

##INIT GLOBALS##

addon = xbmcaddon.Addon(id='org.harddevelop.kodi.tv')
home = addon.getAddonInfo('path')
icon = xbmc.translatePath( os.path.join( home, 'icon.png' ) )
MAIN_URL = xbmcplugin.getSetting(int(sys.argv[1]), "remote_repository")

##CONSTANTS PARTS##
BROWSE_CHANNELS = "browse_channels"

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		cleanedparams=params.replace('?','')
		if (params[len(params)-1]=='/'):
			params=params[0:len(params)-2]
		pairsofparams=cleanedparams.split('&')
		param={}
		for i in range(len(pairsofparams)):
			splitparams={}
			splitparams=pairsofparams[i].split('=')
			if (len(splitparams))==2:
				param[splitparams[0]]=splitparams[1]

	return param

def add_dir(name,url,mode,iconimage,provider,page="", thumbnailImage=''):
	type = "Video"
	#print url
	#print mode
	#print page

	#name = re.sub('[^A-Za-z0-9]+', '',name)
	#print page
	u=sys.argv[0]+"?url="+urllib.quote_plus(url.decode('utf-8', 'replace').encode('iso-8859-1', 'replace'))
	u+="&mode="+str(mode)+"&page="
	try:
		u+=str(page)
	except:
		u+=page
		pass
	provider = str(provider)
	u+="&provider="+provider

	ok=True

	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setInfo(type='Video', infoLabels={'Title': name})

	if mode == 2 or (mode >=100 and mode<=108): #playable, not browser call, needs decoded to be playable or rtmp to be obtained
		liz.setProperty("IsPlayable", "true")
		liz.setPath(url)
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=False) #Playable
	else:
		liz.setProperty('Fanart_Image', thumbnailImage)
		ok=xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz,isFolder=True) #Folder

	return ok

def get_main_dirs():
	add_dir(addon.getLocalizedString(10001), MAIN_URL, 1, icon,'', 0)
	add_dir(addon.getLocalizedString(10010), BROWSE_CHANNELS, 3, '', icon, 0)
	try:
		if updater.isUpdatable():
			add_dir(addon.getLocalizedString(10011), '', 0, icon, 0)
	except:
		logger.error("Couldn't add update option: probably server is down!")

def get_dirs(url,name,page):
	#print "using url: "+url
	response = urllib2.urlopen(url)
	html = response.read()
	if url.endswith(".xml"): #main channels, it's a list to browse
		lists = common.parseDOM(html,"list")
		for item in lists:
			name = common.parseDOM(item,"name")[0].encode("utf-8")
			value = common.parseDOM(item,"url")[0].encode("utf-8")
			add_dir(name, value, 1, icon,'', 0)
	else: #it's the final list channel, split
		bruteChannels = html.split("#EXTINF")
		for item in bruteChannels:
			item = item[item.find(",")+1:]
			name = item[:item.find("\n")]
			value = item[item.find("\n")+1:]
			value = value[:value.find("\n")]
			#print "detected channel: "+name+" with url: "+value
			if name <> "" and value <> "": ##check for empty channels, we don't want it in our list
				add_dir(name, value, 2, icon, '', name)
	
def open(url,page):
	listitem = xbmcgui.ListItem(page)
	listitem.setProperty('IsPlayable','true')
	listitem.setPath(url)
	listitem.setInfo("video",page)
	try:
		player = xbmc.Player(xbmc.PLAYER_CORE_AUTO)
		if player.isPlaying() :
			player.stop()
		#xbmc.sleep(1000)
		player.showSubtitles(False)
		#urlPlayer = urllib.unquote_plus(url.replace("+","@#@")).replace("@#@","+")
		#urlPlayer = urllib.unquote_plus(url) ##THIS METHOD FAILS IN SOME CASES SHOWING A POPUP (server petition and ffmpeg internal problem)
		#player.play(urlPlayer,listitem) ##THIS METHOD FAILS IN SOME CASES SHOWING A POPUP (server petition and ffmpeg internal problem)
		#print 'opening... '+url
		xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, listitem) ##FIX FOR PREVIEWS LINE##
		#xbmc.executebuiltin('Dialog.Close(all, true)') ## could be returned an empty element in a list, so player open the next and shows a invalid popup
	except:
		pass
		#print(traceback.format_exc())

def browse_channels(url,page): #BROWSES ALL PROVIDERS
	add_dir("Filmon.com", 'filmon', 4, "http://static.filmon.com/theme/img/filmon_small_logo.png", 'filmoncom', 0)
	add_dir("HDFull.tv", 'hdfulltv', 4, "http://hdfull.tv/templates/hdfull/images/logo.png", 'hdfulltv' , 0)
	add_dir("Zoptv.com", 'zoptv', 4, "http://www.zoptv.com/images/logo.png", 'zoptv' , 0)
	add_dir("Cineestrenostv.tv", 'cineestrenos', 4, "http://i.imgur.com/z3CINCU.jpg", 'cineestrenos' , 0)
	add_dir("Cricfree.tv", 'cricfree', 4, "http://cricfree.tv/images/logosimg.png", 'cricfree' , 0)
	add_dir("Sports4u.tv", 'sports4u', 4, "http://live.sports4u.tv/wp-content/uploads/logo3.png", 'sports4u' , 0)
	add_dir("Live9.net", 'live9', 4, "", 'live9' , 0)
	add_dir("Vipgoal.net", 'vigoal', 4, "http://vipgoal.net/VIPgoal/img/logo.png", 'vigoal' , 0) #this page was down, TODO: it will be replaced with the new version of this page: verliga.net
	add_dir("Vipracing.info", 'vipracinginfo', 4, "", 'vipracinginfo' , 0)
	add_dir("Skylinewebcams.com", 'skylinewebcams', 4, "http://www.skylinewebcams.com/website.jpg", 'skylinewebcams' , 0)
	add_dir("Hdfullhd.eu", 'hdfullhdeu', 4, "", 'hdfullhdeu' , 0)

def browse_channel(url,page,provider): #MAIN TREE BROWSER IS HERE!
	i = 0
	if provider == "filmoncom":
		jsonChannels = Filmoncom.getChannelsJSON()
		for itemFirst in jsonChannels:
			#print itemFirst
			if page == "0":
				i+=1
				add_dir(itemFirst["title"],"http://www.filmon.com/tv/"+itemFirst["alias"],4,icon,"filmoncom",itemFirst["title"])
			elif (page == itemFirst["title"]) and itemFirst.has_key("channels") :
				for item in itemFirst["channels"]:
					i+=1
					add_dir(item["title"],"http://www.filmon.com/tv/"+item["alias"],5,item["logo"],"filmoncom",item["title"])
			else:
				logger.info("no channel: "+page)
	elif provider== "hdfulltv":
		#print "hdfulltv found"
		#print page
		mode = 4 #continue browsing
		jsonChannels = HdfullTv.getChannels(page)
		#print jsonChannels
		for itemFirst in jsonChannels:
			#print itemFirst
			if itemFirst.has_key("permalink"):
				i+=1
				#print itemFirst
				if itemFirst.has_key("show"): #serie
					link = "http://hdfull.tv/serie/"+itemFirst["permalink"]+"/temporada-"+itemFirst["season"]+"/episodio-"+itemFirst["episode"] #TODO, recheck
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
					else:
						link = "http://hdfull.tv/"+itemFirst["permalink"] #TODO, review
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
				#print image

			add_dir(title,link,mode,image,"hdfulltv",link)
	elif provider == "vigoal":
		jsonChannels = Vigoal.getChannels(page)
		for item in jsonChannels:
			title = item["title"]
			if title=='Display by event':
				title = addon.getLocalizedString(10006)
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
	elif provider == "cineestrenos":
		jsonChannels = Cineestrenostv.getChannels(page)
		for item in jsonChannels:
			title = item["title"]
			link = item["link"]
			#if item.has_key("permalink"):
			mode = 102 #next step returns a final link
			#else:
			#	mode = 4 #continue browsing
			if item.has_key("thumbnail"):
				image = item["thumbnail"]
			else:
				image = icon
			add_dir(title,link,mode,image,"cineestrenos",link)
	elif provider == "cricfree":
		jsonChannels = Cricfreetv.getChannels(page)
		for item in jsonChannels:
			title = item["title"]
			link = item["link"]
			#if item.has_key("permalink"):
			mode = 103 #next step returns a final link
			#else:
			#	mode = 4 #continue browsing
			if item.has_key("thumbnail"):
				image = item["thumbnail"]
			else:
				image = icon
			add_dir(title,link,mode,image,"cricfree",link)
	elif provider == 'zoptv':
		jsonChannels = Zoptvcom.getChannels(page)
		for item in jsonChannels:
			title = item["title"]
			if title=='Browse by Country':
				title = addon.getLocalizedString(10007)
			elif title=='Browse by Genre':
				title = addon.getLocalizedString(10008)
			link = item["link"]
			mode = 4
			if item.has_key("thumbnail"):
				image = item["thumbnail"]
				mode = 104
			else:
				image = icon
			add_dir(title,link,mode,image,"zoptv",link)
	elif provider == 'live9':
		jsonChannels = Live9net.getChannels(page)
		for item in jsonChannels:
			title = item["title"]
			link = item["link"]
			#if item.has_key("permalink"):
			mode = 105 #next step returns a final link
			#else:
			#	mode = 4 #continue browsing
			if item.has_key("thumbnail"):
				image = item["thumbnail"]
			else:
				image = icon
			add_dir(title,link,mode,image,"live9",link)
	elif provider == 'sports4u':
		jsonChannels = Sports4u.getChannels(page)
		for item in jsonChannels:
			title = item["title"]
			link = item["link"]
			#if item.has_key("permalink"):
			mode = 106 #next step returns a final link
			#else:
			#	mode = 4 #continue browsing
			if item.has_key("thumbnail"):
				image = item["thumbnail"]
			else:
				image = icon
			add_dir(title,link,mode,image,"sports4u",link)
	elif provider == 'vipracinginfo':
		jsonChannels = Vipracinginfo.getChannels(page)
		mode = 107
		for item in jsonChannels:
			title = item["title"]
			link = item["link"]
			add_dir(title,link,mode,icon,"vipracinginfo",link)
	elif provider == 'hdfullhdeu':
		jsonChannels = Hdfullhdeu.getChannels(page)
		mode = 4
		for item in jsonChannels:
			title = item["title"]
			link = item["link"]
			if item.has_key("permaLink"):
				mode = 2
			add_dir(title,link,mode,icon,"hdfullhdeu",link)

	elif provider == 'skylinewebcams':
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
	logger.info(provider)

def open_channel(url,page,provider=""):
	finalUrls = Filmoncom.getChannelUrl(url)
	for finalUrl in finalUrls:
		add_dir(page+", "+finalUrl["name"],finalUrl["url"],2,provider,page)
		#print("page: "+page+", url: "+finalUrl["url"])

def init():
	params=get_params()

	url=""
	mode=None
	page=""

	try:
		page=urllib.unquote_plus(params["page"])
	except:
		pass
	try:
		url=urllib.unquote_plus(params["url"])
	except:
		pass
	try:
		mode=int(params["mode"])
	except:
		pass
	try:
		provider=urllib.unquote_plus(params["provider"])
	except:
		pass

	#print "Mode: "+str(mode)
	#print "URL: "+str(url)
	#print "page: "+str(page)

	if mode==None: #init
		get_main_dirs()

	elif mode==1: #get channels
		get_dirs(url, '', page)

	elif mode == 2: #open video in player
		open(url,page)
	elif mode == 3:
		browse_channels(url,page)
	elif mode == 4:
		browse_channel(url,page,provider)
	elif mode == 5:
		open_channel(url,page)
	elif mode == 0: #update
		updater.update()
		get_main_dirs()
	elif mode == 100: #decode provider link
		logger.info("decoding: "+url)
		link = Decoder.decodeLink(url)
		logger.info("decoded: "+link)
		open(link,page)
	elif mode == 101:
		jsonChannels = Vigoal.getChannels(page)
		url = jsonChannels[0]["link"]
		logger.info("found link: "+url+", launching...")
		open(url,page) #same that 2, but reserved for rtmp
	elif mode == 102:
		jsonChannels = Cineestrenostv.getChannels(page)
		url = jsonChannels[0]["link"]
		logger.info("found link: "+url+", launching...")
		open(url,page)
	elif mode == 103:
		channel = Cricfreetv.getChannels(page)
		logger.info("found link: "+channel[0]["link"]+", launching...")
		open(channel[0]["link"],page)
	elif mode == 104:
		channel = Zoptvcom.getChannels(page)
		logger.info("found link: "+channel[0]["link"]+", launching...")
		open(channel[0]["link"],page)
	elif mode == 105:
		channel = Live9net.getChannels(page)
		logger.info("found link: "+channel[0]["link"]+", launching...")
		open(channel[0]["link"],page)
	elif mode == 106:
		channel = Sports4u.getChannels(page)
		logger.info("found link: "+channel[0]["link"]+", launching...")
		open(channel[0]["link"],page)
	elif mode == 107:
		channel = Vipracinginfo.getChannels(page)
		logger.info("found link: "+channel[0]["link"]+", launching...")
		open(channel[0]["link"],page)
	elif mode == 108:
		channel = Skylinewebcamscom.getChannels(page)
		logger.info("found link: "+channel[0]["link"]+", launching...")
		open(channel[0]["link"],page)
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

init()