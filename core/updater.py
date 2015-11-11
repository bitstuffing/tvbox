import urllib2,os,sys
import xbmcplugin
import xbmcaddon
import xbmc
from core import logger
from core import downloadtools
from core import ziptools
import time
import CommonFunctions as common

REMOTE_FILE_XML = xbmcplugin.getSetting(int(sys.argv[1]), "remote_updater")

ROOT_DIR = xbmcaddon.Addon(id='org.harddevelop.kodi.tv').getAddonInfo('path')

def update():
    #download ZIP file
    start = time.clock()

    localfile = ROOT_DIR+"/update.zip"

    response = urllib2.urlopen(REMOTE_FILE_XML)
    html = response.read()
    remote_file = common.parseDOM(html,"file")[0].encode("utf-8") #remote version
    downloadtools.downloadfile(remote_file, localfile, notStop=False)

    end = time.clock()
    logger.info("org.harddevelop.kodi.tv Downloaded in %d seconds " % (end-start+1))

    #unzip
    unzipper = ziptools.ziptools()
    logger.info("org.harddevelop.kodi.tv destpathname=%s" % ROOT_DIR)
    addons_dir = ROOT_DIR[:ROOT_DIR.rfind('/')+1]
    current_plugin_dir = ROOT_DIR[ROOT_DIR.rfind('/')+1:]
    logger.debug("using dir: "+addons_dir+" to extract content")

    unzipper.extractReplacingMainFolder(localfile,addons_dir,current_plugin_dir) #github issues
    #unzipper.extract(localfile,ROOT_DIR)

    #clean downloaded zip file
    logger.info("org.harddevelop.kodi.tv clean zip file...")
    os.remove(localfile)
    logger.info("org.harddevelop.kodi.tv clean done!")

def isUpdatable():
    #remote file
    response = urllib2.urlopen(REMOTE_FILE_XML)
    html = response.read()
    remote_version = common.parseDOM(html,"version")[0].encode("utf-8") #remote version
    #local file
    fp = open(ROOT_DIR+"/version.xml", "r")
    content = fp.read()
    fp.close()
    local_version = common.parseDOM(content,"version")[0].encode("utf-8") #remote version
    print "localversion: "+local_version+", remoteversion: "+remote_version
    return bool(int(local_version)<int(remote_version))