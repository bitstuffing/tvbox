# -*- coding: utf-8 -*-

import CommonFunctions as common
import urllib
import urllib2
import os,sys
import xbmc
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
from providers.zonasportsme import Zonasportsme
from providers.sportstream365com import Sportstream365com
from providers.showsporttvcom import ShowsportTvCom
from providers.mamahdcom import Mamahdcom
from providers.arenavisionin import Arenavisionin
splive = True
try:
	from providers.spliveappcom import Spliveappcom
except:
	splive = False
	logger.error("Crypto-problems detected, probably you need better environment")
	pass
from core.downloader import Downloader
from core.decoder import Decoder
import re
import platform

##INIT GLOBALS##

addon = xbmcaddon.Addon(id='org.harddevelop.kodi.tv')
home = addon.getAddonInfo('path')
icon = xbmc.translatePath( os.path.join( home, 'icon.png' ) )
MAIN_URL = xbmcplugin.getSetting(int(sys.argv[1]), "remote_repository")

##CONSTANTS PARTS##
BROWSE_CHANNELS = "browse_channels"
MAX = 114

def get_params():
	param=[]
	paramstring=sys.argv[2]
	if len(paramstring)>=2:
		params=sys.argv[2]
		try:
			#now extract expected params, it has been changed because some params could be links
			#with other params and the previews method (split with '?' expr. doesn't work in some cases)
			logger.debug("filling params array with brute params...")
			mode = params[params.find("mode=")+len("mode="):]
			logger.debug("brute mode: "+mode)
			if mode.find("&")>-1:
				mode = mode[:mode.find("&")]
			url = params[params.find("url=")+len("url="):]
			logger.debug("brute url: "+url)
			if url.find("&mode")>-1:
				url = url[:url.find("&mode")]
			elif url.find("&page")>-1:
				url = url[:url.find("&page")]
			elif url.find("&")>-1:
				url = url[:url.find("&")]
			page = params[params.find("page=")+len("page="):]
			logger.debug("brute page: "+page)
			if page.find("&provider")>-1:
				page = page[:page.find("&provider")]
			elif page.find("&")>-1:
				page = page[:page.find("&")]
			provider = params[params.find("provider=")+len("provider="):]
			logger.debug("brute provider: "+provider)
			if provider.find("&")>-1:
				provider = provider[:provider.find("&")]
			#finally put in param array
			logger.debug("done, filling params dic...")
			param={}
			param["mode"] = mode
			param["url"] = url
			param["page"] = page
			param["provider"] = provider
			logger.debug("done params built: "+str(len(param)))
		except Exception as e:
			logger.error("ERROR: using old method to extract params..."+str(e))
			#old method
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
					logger.info("param: "+splitparams[0]+" with value: "+splitparams[1])

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
	u+="&provider="+urllib.quote_plus(provider.decode('utf-8', 'replace').encode('iso-8859-1', 'replace'))

	ok=True

	liz=xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
	liz.setInfo(type='Video', infoLabels={'Title': name})

	if mode == 2 or (mode >=100 and mode<=MAX): #playable, not browser call, needs decoded to be playable or rtmp to be obtained
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
	html = Downloader.getContentFromUrl(url)
	if url.endswith(".xml"): #main channels, it's a list to browse
		lists = common.parseDOM(html,"list")
		if len(lists)>0:
			logger.info("counted: "+str(len(lists)))
			for item in lists:
				name = common.parseDOM(item,"name")[0].encode("utf-8")
				value = common.parseDOM(item,"url")[0].encode("utf-8")
				logger.info("Added: "+name+", url: "+value)
				add_dir(name, value, 1, icon,'', 0)
		else:
			lists = common.parseDOM(html,"item") #sportsdevil private lists
			if len(lists)>0:
				for item in lists:
					name = common.parseDOM(item,"title")[0].encode("utf-8")
					value = common.parseDOM(item,"sportsdevil")[0].encode("utf-8")
					referer = ""
					try:
						referer = common.parseDOM(item,"referer")[0].encode("utf-8")
					except:
						logger.info("referer not found!")
					img = icon
					try:
						img = common.parseDOM(item,"thumbnail")[0].encode("utf-8")
					except:
						logger.info("thumbnail not found!")
					if name!="" and value!="":
						if referer!= "":
							value +=", referer: "+referer
						logger.info("Added: "+name+", url: "+value)
						add_dir(name, value, 2, img,'', 0)
	else: #it's the final list channel, split
		bruteChannels = html.split("#EXTINF")
		for item in bruteChannels:
			item = item[item.find(",")+1:]
			name = item[:item.find("\n")]
			value = item[item.find("\n")+1:]
			value = value[:value.find("\n")]
			#print "detected channel: "+name+" with url: "+value
			if name != "" and value != "": ##check for empty channels, we don't want it in our list
				add_dir(name, value, 2, icon, '', name)
	
def open(url,page):
	if url.find("rtmp://")==-1 and url.find("|Referer=")==-1 and ( url.find("http://privatestream.tv/")>-1 or url.find("http://www.dinostream.pw/")>-1 or url.find("http://www.embeducaster.com/")>-1 or url.find("http://tv.verdirectotv.org/channel.php")>-1 or url.find("http://mamahd.com/")>-1):
		logger.info("brute url [referer] is: "+url)
		referer = ''
		if(url.find("referer: ")>-1):
			referer = url[url.find("referer: ")+len("referer: "):]
		url = url[0:url.find(",")]
		if url.find("http://privatestream.tv/")>-1:
			html = Downloader.getContentFromUrl(url,"","",referer)
			url = Decoder.decodePrivatestream(html,referer)
		elif url.find("http://www.dinostream.pw/")>-1:
			url = Decoder.extractDinostreamPart(url,referer)["link"]
		elif url.find("http://www.embeducaster.com/")>-1:
			#url = url.replace("/membedplayer/","/embedplayer/")
			url = Cineestrenostv.getContentFromUrl(url,"","",referer)
		elif url.find("http://tv.verdirectotv.org/channel.php")>-1:
			html4 = Cineestrenostv.getContentFromUrl(url,"",Cineestrenostv.cookie,referer)
			finalIframeUrl = Decoder.extractWithRegex('http://','%3D"',html4)
			if finalIframeUrl.find('"')>-1 or finalIframeUrl.find("'")>-1:
				finalIframeUrl = finalIframeUrl[0:len(finalIframeUrl)-1]
			finalHtml = Cineestrenostv.getContentFromUrl(finalIframeUrl,"",Cineestrenostv.cookie,referer)
			url = Decoder.decodeBussinessApp(finalHtml,finalIframeUrl)
		elif url.find("http://mamahd.com/")>-1:
			url = Mamahdcom.getChannels(url)[0]["link"]
		elif url.find("http://showsport-tv.com/")>-1:
			url = ShowsportTvCom.getChannels(url)[0]["link"]
	elif url.find("rtmp://")==-1:
		try:
			if url.find(", referer: ")>-1:
				page = url[url.find(", referer: ")+len(", referer: "):]
				url = url[:url.find(", referer: ")]
				logger.debug("changing page to referer: "+page)
			logger.debug("trying decoder part for url: "+url)
			url = Decoder.decodeLink(url,page)
		except:
			logger.info("decoder url launched an exception, probably could not be decoded")
			pass
	#launch redirects to his better addons
	if url.find("sop://")>-1 or url.find("acestream://")>-1: #required plexus or something similar installed, this dependency is external from this addon so needs to be installed
		logger.info("trying to send link to plexus: "+url)
		mode = "1"
		if url.find("sop://")>-1:
			mode = "2"
		url = "plugin://program.plexus/?mode="+mode+"&url="+url+"&name=RemoteLink"
	elif url.find(".torrent")>-1 or url.find("magnet:")>-1:
		logger.info("trying to send link to quasar: "+url)
		url = urllib.quote_plus(url)
		url = "plugin://plugin.video.quasar/play?uri="+url
	elif url.find("youtube.com/")>-1:
		id = ""
		if url.find("v=")>-1:
			id = url[url.find("v=")+len("v="):]
		elif url.find("/embed/")>-1:
			id = url[url.find("/embed/")+len("/embed/"):]
		url = "plugin://plugin.video.youtube/play/?video_id="+id+""
	elif url.find("vimeo.com/")>-1:
		url = "plugin://plugin.video.youtube/play/?video_id="+urllib.quote_plus(url)
	else:
		logger.info("nothing done!")
	logger.debug("launching playable url: "+url)
	play(url,page)

def play(url,page):
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

def browse_channels(url,page): #BROWSES ALL PROVIDERS (it has been re-sorted)
	#static content
	add_dir("HDFull.tv", 'hdfulltv', 4, "http://hdfull.tv/templates/hdfull/images/logo.png", 'hdfulltv' , 0)
	enableSplive = xbmcplugin.getSetting(int(sys.argv[1]), "enable_splive")
	if enableSplive=="true" and splive:
		add_dir("Spliveapp.com", 'splive', 4, "http://www.spliveapp.com/main/wp-content/uploads/footer_logo.png", 'splive' , 0)
	enablePlexus = xbmcplugin.getSetting(int(sys.argv[1]), "enable_plexus")
	if enablePlexus=="true":
		add_dir("Arenavision.in", 'arenavisionin', 4, "http://www.arenavision.in/sites/default/files/logo_av2015.png", 'arenavisionin' , 0)
	#sports with event
	patchedFfmpeg = xbmcplugin.getSetting(int(sys.argv[1]), "ffmpeg_patch")
	if patchedFfmpeg=="true":
		add_dir("Vipgoal.net", 'vigoal', 4, "http://vipgoal.net/VIPgoal/img/logo.png", 'vigoal' , 0)
	add_dir("Live9.net", 'live9', 4, "", 'live9' , 0)
	#add_dir("Sportstream365.com", 'sportstream365com', 4, "http://sportstream365.com/img/logo.png", 'sportstream365com' , 0)
	#sports without event (at least not implemented yet)
	add_dir("Mamahd.com", 'mamahdcom', 4, "http://mamahd.com/images/logo.png", 'mamahdcom' , 0)
	#world tv
	if patchedFfmpeg=="true":
		add_dir("Cinestrenostv.tv", 'cineestrenos', 4, "http://i.imgur.com/z3CINCU.jpg", 'cineestrenos' , 0) #TODO, put in settings a download and install ffmpeg patched by platform
	add_dir("Filmon.com", 'filmon', 4, "http://static.filmon.com/theme/img/filmon_small_logo.png", 'filmoncom', 0)
	add_dir("Zoptv.com", 'zoptv', 4, "http://www.zoptv.com/images/logo.png", 'zoptv' , 0)
	add_dir("Cricfree.tv", 'cricfree', 4, "http://cricfree.tv/images/logosimg.png", 'cricfree' , 0)
	add_dir("Zonasports.me", 'zonasportsme', 4, "http://i.imgur.com/yAuKRZw.png", 'zonasportsme' , 0)
	add_dir("Sports4u.tv", 'sports4u', 4, "http://live.sports4u.tv/wp-content/uploads/logo3.png", 'sports4u' , 0)
	add_dir("Showsport-tv.com", 'showsporttvcom', 4, "http://showsport-tv.com/images/logoh.png", 'showsporttvcom' , 0)
	add_dir("Vipracing.net", 'vipracinginfo', 4, "", 'vipracinginfo' , 0)
	#static streaming lists
	add_dir("Hdfullhd.eu", 'hdfullhdeu', 4, "", 'hdfullhdeu' , 0)
	#webcams and others
	add_dir("Skylinewebcams.com", 'skylinewebcams', 4, "http://www.skylinewebcams.com/website.jpg", 'skylinewebcams' , 0)


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
	#print "hdfulltv found"
	#print page
	mode = 4 #continue browsing
	jsonChannels = HdfullTv.getChannels(page)
	#print jsonChannels
	for itemFirst in jsonChannels:
		#print itemFirst
		if itemFirst.has_key("permalink"):
			#print itemFirst
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

def drawVipgoal(page):
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
			title = addon.getLocalizedString(10006)
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
	for item in jsonChannels:
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
			title = addon.getLocalizedString(10006)
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
			title = addon.getLocalizedString(10006)
		link = item["link"]
		if link!='1':
			mode = 114
		if item.has_key("thumbnail"):
			image = item["thumbnail"]
			logger.info("detected img: "+image)
		else:
			image = icon
		add_dir(title,link,mode,image,"arenavisionin",link)

def browse_channel(url,page,provider): #MAIN TREE BROWSER IS HERE!
	if provider == "filmoncom":
		drawFilmon(page)
	elif provider== "hdfulltv":
		drawHdfulltv(page)
	elif provider == "vigoal":
		drawVipgoal(page)
	elif provider == "cineestrenos":
		drawCinestrenostv(page)
	elif provider == "cricfree":
		drawCricfree(page)
	elif provider == 'zoptv':
		drawZoptv(page)
	elif provider == 'live9':
		drawLive9(page)
	elif provider == 'sports4u':
		drawSports4u(page)
	elif provider == 'vipracinginfo':
		drawVipracinginfo(page)
	elif provider == 'hdfullhdeu':
		drawHdfullhdeu(page)
	elif provider == 'skylinewebcams':
		drawSkylinewebcams(page)
	elif provider == 'zonasportsme':
		drawZonasportsme(page)
	elif provider == 'sportstream365com':
		drawSportstream365(page)
	elif provider == 'splive':
		drawSplive(page)
	elif provider == 'mamahdcom':
		drawMamahdcom(page)
	elif provider == 'showsporttvcom':
		drawShowsporttvcom(page)
	elif provider == 'arenavisionin':
		drawArenavisionin(page)
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
	provider = ""

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

	logger.debug("Mode: "+str(mode))
	logger.debug("URL: "+str(url))
	logger.debug("page: "+str(page))
	logger.debug("provider: "+str(provider))

	try:

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
			if xbmcgui.Dialog().yesno(addon.getLocalizedString(10011),updater.getUpdateInfo(), "", "", addon.getLocalizedString(11013), addon.getLocalizedString(11014) ):
				updater.update()
			get_main_dirs()
		elif mode == 97:
			masterPatchUrl = "https://github.com/harddevelop/httpproxy-service/archive/master.zip"
			try:
				updater.install(masterPatchUrl,"org.harddevelop.kodi.proxy","org.harddevelop.kodi.proxy")
				xbmcgui.Dialog().ok(addon.getLocalizedString(30060),addon.getLocalizedString(30060))
				logger.debug("patch installed!")
			except:
				logger.error("Patch not installed, something wrong happened!")
				pass
		elif mode == 98:
			if xbmcgui.Dialog().yesno(addon.getLocalizedString(30052),addon.getLocalizedString(30052), "", "", addon.getLocalizedString(11011), addon.getLocalizedString(11010) ):
				quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/archive/master.zip"
				if xbmc.getCondVisibility( "system.platform.windows" ):
					logger.debug("Detected Windows system...")
					if "x64" in platform.machine():
						quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.windows_x64.zip"
					else:
						quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.windows_x86.zip"
				elif xbmc.getCondVisibility( "System.Platform.Android" ):
					logger.debug("Detected Android system...")
					if os.uname()[4].startswith("arm"):
						logger.debug("android system...")
						quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.android_arm.zip"
					else:
						logger.debug("Androidx86 system...")
						quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.android_x86.zip"
				elif xbmc.getCondVisibility("System.Platform.Linux.RaspberryPi"):
					logger.debug("raspberry system...")
					if "armv7" in platform.machine():
						logger.debug("raspberry pi 2!")
						quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.linux_armv7.zip"
					elif "armv6" in platform.machine():
						logger.debug("raspberry pi 1!")
						quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.linux_arm.zip"
					else:
						logger.debug("raspberry pi 3!")
						quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.linux_arm64.zip"
				elif xbmc.getCondVisibility("System.Platform.Linux"):
					if "x64" in platform.machine():
						quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.linux_x64.zip"
					else:
						quasarUrl = "https://github.com/scakemyer/plugin.video.quasar/releases/download/v0.9.34/plugin.video.quasar-0.9.34.linux_x86.zip"
				else:
					logger.info("no detected platform, using default (could be a osx?)")
				try:
					updater.install(quasarUrl,"plugin.video.quasar","plugin.video.quasar")
					logger.debug("addon installed!")
				except:
					logger.error("Addon not installed, something wrong happened!")
					pass
				xbmcgui.Dialog().ok(addon.getLocalizedString(30051),addon.getLocalizedString(30051))
				logger.debug("launch done!")
		elif mode == 99:
			if xbmcgui.Dialog().yesno(addon.getLocalizedString(30050),addon.getLocalizedString(30050), "", "", addon.getLocalizedString(11011), addon.getLocalizedString(11010) ):
				try:
					#url = "http://repo.adryanlist.org/program.plexus-0.1.4.zip"
					url = "https://github.com/AlexMorales85/program.plexus/archive/1.2.2.zip" #better and updated with an acestream fixed client for raspberry platforms
					updater.install(url,"program.plexus","program.plexus")
					logger.debug("addon installed!")
					#try with request dependency
					updater.install("https://github.com/beenje/script.module.requests/archive/gotham.zip","script.module.requests","script.module.requests")
					logger.debug("dependency installed, finished!")
				except:
					logger.error("Addon not installed, something wrong happened!")
					pass
				xbmcgui.Dialog().ok(addon.getLocalizedString(30051),addon.getLocalizedString(30051))
				logger.debug("launch done!")
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
		elif mode == 109:
			channel = Zonasportsme.getChannels(url)
			logger.info("found link: "+channel[0]["link"]+", launching...")
			open(channel[0]["link"],page)
		elif mode == 110:
			channel = Sportstream365com.getChannels(url)
			logger.info("found link: "+channel[0]["link"]+", launching...")
			open(channel[0]["link"],page)
		elif mode == 111:
			if url.find(".m3u8")==-1 and url.find("rtmp://")==-1:
				channel = Spliveappcom.decodeUrl(url,provider)
				link = channel[0]["link"]
			else:
				link = url
			logger.info("found link: "+link+", launching...")
			open(link,page)
		elif mode == 112:
			channel = Mamahdcom.getChannels(url)
			logger.info("found link: "+channel[0]["link"]+", launching...")
			open(channel[0]["link"],page)
		elif mode == 113:
			channel = ShowsportTvCom.getChannels(url)
			logger.info("found link: "+channel[0]["link"]+", launching...")
			open(channel[0]["link"],page)
		elif mode == 114:
			channel = Arenavisionin.getChannels(url)
			logger.info("found link: "+channel[0]["link"]+", launching...")
			open(channel[0]["link"],page)
	except Exception as e:
		logger.error(addon.getLocalizedString(10009)+", "+str(e))
		xbmcgui.Dialog().notification("Error",addon.getLocalizedString(10009))
		pass
	xbmcplugin.endOfDirectory(int(sys.argv[1]))

init()