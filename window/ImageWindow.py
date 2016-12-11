import xbmcgui
import xbmc
import xbmcaddon
import json
import sys
from PIL import Image
from core.xbmcutils import XBMCUtils
from core.downloadtools import downloadfile
from core import logger

ROOT_DIR = XBMCUtils.getAddonInfo('path')

class windowImage(xbmcgui.WindowDialog):
    def __init__(self):

        window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        window.setProperty('ShowImage', 'true')

        # check arg getting from settings
        try:
            idImage = str(sys.argv[1])
        except:
            idImage = '0'

        window = xbmcgui.Window(xbmcgui.getCurrentWindowId())
        imagePath = window.getProperty('imagePath')
        logger.debug("imagePath property: "+str(imagePath))

        # set max height and margin to background
        xImageRes = 660
        yImageRes = 400
        yMax = 660
        margin = 10

        if idImage == '0':
            msg = "Code 0 message"
        elif imagePath == '':
            msg = "Other codes different from 0"
        else:
            try:
                logger.debug("trying to download image from: "+imagePath)
                imageName = imagePath[imagePath.rfind("/"):]
                localfile = ROOT_DIR + imageName
                downloadfile(url=imagePath,fileName=localfile)
                logger.debug("trying to open image in window: "+localfile)
                image = Image.open(localfile)
                logger.debug("finished: " + localfile)
                msg = ''
            except:
                msg = "Exception message"
                logger.error("Something goes wrong trying to obtain remote image inside ImageWindow class")
            else:
                imageSize = image.size
                xImageRes = imageSize[0]
                yImageRes = imageSize[1]

        # scale if image is too big
        if yImageRes > yMax:
            scale = (xImageRes) / float(yImageRes)

            xImageRes = int(scale * yMax)
            yImageRes = yMax

        # set size
        xImagePos = ((1280 - xImageRes) / 2)
        yImagePos = ((720 - yImageRes) / 2) - margin
        xBgRes = xImageRes + (margin * 2)
        yBgRes = yImageRes + (margin * 4)
        xBgPos = xImagePos - margin
        yBgPos = yImagePos - margin

        # create window
        self.bg = xbmcgui.ControlImage(xBgPos, yBgPos, xBgRes, yBgRes, ROOT_DIR+'/images/bg.png')
        self.addControl(self.bg)
        if msg == '':
            self.image = xbmcgui.ControlImage(xImagePos, yImagePos, xImageRes, yImageRes, imagePath)
            self.addControl(self.image)
        else:
            self.label = xbmcgui.ControlLabel(xImagePos, yImagePos, xImageRes, yImageRes, msg, 'font13', alignment=6)
            self.addControl(self.label)

    def onAction(self, action):
        self.close()

    def onControl(self, control):
        self.close()