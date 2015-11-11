import sys, os.path
import re
import urllib,urllib2
import time
import socket
import logger
import xbmc
import xbmcaddon
import xbmcgui
import traceback # for download problems
import StringIO
import gzip

addon = xbmcaddon.Addon(id='org.harddevelop.kodi.tv')

def sec_to_hms(seconds):
    m,s = divmod(int(seconds), 60)
    h,m = divmod(m, 60)
    return ("%02d:%02d:%02d" % ( h , m ,s ))

def downloadfile(url,fileName,headers=[],silent=False,notStop=False):
    logger.info("[downloadtools.py] downloadfile: url="+url)
    logger.info("[downloadtools.py] downloadfile: fileName="+fileName)

    try:

        try:
            fileName = xbmc.makeLegalFilename(fileName)
        except:
            pass
        logger.info("[downloadtools.py] downloadfile: fileName="+fileName)

        if os.path.exists(fileName) and notStop:
            f = open(fileName, 'r+b')
            existSize = os.path.getsize(fileName)
            
            logger.info("[downloadtools.py] downloadfile: file exists, size=%d" % existSize)
            recordedSize = existSize
            f.seek(existSize)

        elif os.path.exists(fileName) and not notStop:
            logger.info("[downloadtools.py] downloadfile: file exists, dont re-download")
            return

        else:
            existSize = 0
            logger.info("[downloadtools.py] downloadfile: file doesn't exists")

            f = open(fileName, 'wb')
            recordedSize = 0

        if not silent:
            progressDialog = xbmcgui.DialogProgress() # Open dialog
            progressDialog.create( "plugin" , addon.getLocalizedString(10002) , url , fileName )
        else:
            progressDialog = ""

        socket.setdefaulttimeout(30) #Timeout
    
        h=urllib2.HTTPHandler(debuglevel=0)
        request = urllib2.Request(url)
        for header in headers:
            logger.info("[downloadtools.py] Header="+header[0]+": "+header[1])
            request.add_header(header[0],header[1])
    
        if existSize > 0:
            request.add_header('Range', 'bytes=%d-' % (existSize, ))
    
        opener = urllib2.build_opener(h)
        urllib2.install_opener(opener)
        try:
            connection = opener.open(request)
        except: # End
            f.close()
            if not silent:
                progressDialog.close()

    
        try:
            totalFileSize = int(connection.headers["Content-Length"])
        except:
            totalFileSize = 1
                
        if existSize > 0:
            totalFileSize = totalFileSize + existSize
    
        logger.info("Content-Length=%s" % totalFileSize)
    
        blockSize = 100*1024 #Buffer size
    
        bufferReadedSize = connection.read(blockSize)
        logger.info("Starting download, readed=%s" % len(bufferReadedSize))
    
        maxRetries = 5
        
        while len(bufferReadedSize)>0:
            try:
                f.write(bufferReadedSize)
                recordedSize = recordedSize + len(bufferReadedSize)
                percent = int(float(recordedSize)*100/float(totalFileSize))
                totalMB = float(float(totalFileSize)/(1024*1024))
                downloadedMB = float(float(recordedSize)/(1024*1024))

                retries = 0
                while retries <= maxRetries:
                    try:
                        before = time.time()
                        bufferReadedSize = connection.read(blockSize)
                        after = time.time()
                        if (after - before) > 0:
                            speed=len(bufferReadedSize)/((after - before))
                            remainingSize=totalFileSize-recordedSize
                            if speed>0:
                                remainingTime=remainingSize/speed
                            else:
                                remainingTime=0 #infinite

                            if not silent:
                                progressDialog.update( percent , addon.getLocalizedString(10003) % ( downloadedMB , totalMB , percent , speed/1024 , sec_to_hms(remainingTime))) #respect syntax in translations
                        break
                    except:
                        retries = retries + 1
                        logger.info("ERROR downloading buffer, retry %d" % retries)
                        logger.error( traceback.print_exc() )
                
                # if the user stops download proccess...
                try:
                    if progressDialog.iscanceled():
                        logger.info("Download was canceled by user action")
                        f.close()
                        progressDialog.close()
                        return -1
                except:
                    pass
    
                # Something wrong happened
                if retries > maxRetries:
                    logger.info("ERROR, something happened in download proccess")
                    f.close()
                    if not silent:
                        progressDialog.close()
    
                    return -2
    
            except:
                logger.error( traceback.print_exc() )

                f.close()
                if not silent:
                    progressDialog.close()

                return -2

    except:
        xbmcgui.Dialog().ok(addon.getLocalizedString(10004))

    try:
        f.close()
    except:
        pass

    if not silent:
        try:
            progressDialog.close()
        except:
            pass

    logger.info("Finished download proccess")

def downloadfileGzipped(url,filePath):
    logger.info("[downloadtools.py] downloadfileGzipped: url="+url)
    logger.info("[downloadtools.py] downloadfileGzipped: filePath="+filePath)

    fileName = xbmc.makeLegalFilename(filePath)
    logger.info("[downloadtools.py] downloadfileGzipped: fileName="+fileName)
    pattern = "(http://[^/]+)/.+" #seek for url
    matches = re.compile(pattern,re.DOTALL).findall(url)
    
    if len(matches):
        logger.info("[downloadtools.py] MAIN URL :"+matches[0])
        refererUrl= matches[0]
    else:
        refererUrl = url
    
    headers =  {"User-Agent":"Mozilla/5.0 (X11; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0",
                  "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                  "Accept-Language":"en-US,en;q=0.8,es-ES;q=0.5,es;q=0.3",
                  "Accept-Encoding":"gzip,deflate",
                  "Accept-Charset":"ISO-8859-1,utf-8;q=0.7,*;q=0.7",
                  "Cache-Control":"max-age=0",
                  "Connection":"keep-alive",
                  "Referer":refererUrl} #TODO, append Host and Cookie support
        
    progressDialog = xbmcgui.DialogProgress()
    progressDialog.create( "addon" , addon.getLocalizedString(10002), url , fileName )

    # Timeout del socket a 60 segundos
    socket.setdefaulttimeout(10)

    handler=urllib2.HTTPHandler(debuglevel=0) #TODO remove this handler
    request = urllib2.Request(url, '', headers) #TODO, replace "" by list or json array

    opener = urllib2.build_opener(handler)
    urllib2.install_opener(opener)
    try:
        connection = opener.open(request)
    except:
        progressDialog.close()
    baseFileName = os.path.basename(fileName)
    if len(baseFileName) == 0:
        logger.info("extracting filename from response")
        baseName = connection.headers["Content-Disposition"]
        logger.info(baseName)
        pattern = 'filename="([^"]+)"' #replace the other pattern, now seeking for filename
        matches = re.compile(pattern,re.DOTALL).findall(baseName)
        if len(matches)>0:
            title = matches[0]
            fileName = os.path.join(filePath,title)
        else:
            logger.info("filename not found, replacing with noname.txt")
            title = "noname.txt"
            fileName = os.path.join(filePath,title)
    totalFileSize = int(connection.headers["Content-Length"])

    f = open(fileName, 'w')
    
    existSize = 0
    
    logger.info("[downloadtools.py] downloadfileGzipped: new file opened")

    saved = 0
    logger.info("Content-Length=%s" % totalFileSize)

    bufferSize = 100*1024

    bufferReaded = connection.read(bufferSize)
    
    try:
        compressedStream = StringIO.StringIO(bufferReaded)
        gzippedFile = gzip.GzipFile(fileobj=compressedStream)
        data = gzippedFile.read()
        gzippedFile.close()
        xbmc.log("Starting gzipped download file, readed=%s" % len(bufferReaded))
    except:
        xbmc.log( "ERROR : The GZIP file could not been downloaded")
        f.close()
        progressDialog.close()
        return -2
        
    maxRetries = 5
    
    while len(bufferReaded)>0:
        try:
            f.write(data)
            saved = saved + len(bufferReaded)
            percent = int(float(saved)*100/float(totalFileSize))
            totalMB = float(float(totalFileSize)/(1024*1024))
            sizeMB = float(float(saved)/(1024*1024))

            retries = 0
            while retries <= maxRetries:
                try:
                    before = time.time()
                    bufferReaded = connection.read(bufferSize)

                    compressedStream = StringIO.StringIO(bufferReaded)
                    gzippedFile = gzip.GzipFile(fileobj=compressedStream)
                    data = gzippedFile.read()
                    gzippedFile.close()
                    after = time.time()
                    if (after - before) > 0:
                        speed=len(bufferReaded)/((after - before))
                        remaining=totalFileSize-saved
                        if speed>0:
                            remainingTime=remaining/speed
                        else:
                            remainingTime=0
                        logger.info(sec_to_hms(remainingTime))
                        progressDialog.update( percent , addon.getLocalizedString(10003) % ( sizeMB , totalMB , percent , speed/1024 , sec_to_hms(remainingTime)))
                    break
                except:
                    retries = retries + 1
                    logger.info("ERROR downloading buffer, retring %d" % retries)
                    for line in sys.exc_info():
                        logger.error( "%s" % line )

            if progressDialog.iscanceled():
                logger.info("User stop download proccess (GZIP)")
                f.close()
                progressDialog.close()
                return -1

            if retries > maxRetries:
                logger.info("ERROR, something happened in download proccess. Stopped!")
                f.close()
                progressDialog.close()

                return -2

        except:
            logger.info("ERROR, something happened in download proccess.")
            for line in sys.exc_info():
                logger.error( "%s" % line )
            f.close()
            progressDialog.close()
            
            return -2
    f.close()

    progressDialog.close()
    logger.info("Finished GZIP download proccess")
    return fileName
