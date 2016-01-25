import xbmc
import xbmcplugin
import sys

enabled = bool(xbmcplugin.getSetting(int(sys.argv[1]), "debug")=="true")

def info(text):
    if enabled:
        try:
            xbmc.log(text)
        except:
            validChars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
            stripped = ''.join(c for c in text if c in validChars)
            xbmc.log("(stripped) "+stripped)

def debug(text):
    if enabled:
        try:
            xbmc.log(text)
        except:
            validChars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
            stripped = ''.join(c for c in text if c in validChars)
            xbmc.log("(stripped) "+stripped)

def error(text):
    if enabled:
        try:
            xbmc.log(text)
        except:
            validChars = " ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890!#$%&'()-@[]^_`{}~."
            stripped = ''.join(c for c in text if c in validChars)
            xbmc.log("(stripped) "+stripped)


