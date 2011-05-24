import os
import shutil
import logging
import urllib
import time
from Config import Config

logger = logging.getLogger('Testing')
hdlr = logging.FileHandler('./messages.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

def log(msg):
	logger.info(msg)
	print msg

running = True
while running:
	log("Checking for movies")
	for root, dirs, files in os.walk(Config.DL_DIRECTORY):
		for file in files:
			path = os.path.join(root, file)
			size = os.path.getsize(path)
			if (size > Config.MIN_FILE_SIZE):
				
				newpath = os.path.join(Config.MOVIE_DESTINATION, file)
				log("Attempting to rename '" + path + "' to '" + newpath + "'.")
				try:
					os.rename(path, newpath)
					log("Rename of '" + path + "' to '" + newpath + "' successful.")
				except OSError, e:
					error = "Rename (move) unsuccessful. Error %d: %s" % (e.args[0], e.args[1])
					log(error)
				
				log("Attempting to send download complete notification for: " + file)
				notification = Config.XBMC_URL + "/xbmcCmds/xbmcHttp?command=ExecBuiltIn(Notification(" + file + ", Download Complete))"
				try:
					urllib.urlopen(notification)
					log("Download complete notification successfully sent for: " + file)
				except IOError, e:
					error = "Download complete notification unsuccessful. Error %d: %s" % (e.args[0], e.args[1])
					log(error)
				
				updateRpc = '{"jsonrpc": "2.0", "method": "VideoLibrary.ScanForContent", "id": "1"}'
				log("Attemping to update XBMC library.")
				try:
					respdata = urllib.urlopen(Config.JSON_RPC_URL, updateRpc).read()
					log("Update of XBMC library successful.")
				except IOError, e:
					error = "Update of XBMC library unsuccessful. Error %d: %s" % (e.args[0], e.args[1])
	
	for root, dirs, files in os.walk(Config.DL_DIRECTORY):
		if dirs != []:
			for dir in dirs:
				dirPath = os.path.join(root, dir)
				log("Removing directory '" + dirPath + "'")
				shutil.rmtree(dirPath)
	try:
		time.sleep(Config.SLEEP_SECS)
	except Exception, e:
		log("Quitting movie mover script.")
		running = False
	except KeyboardInterrupt, e:
		log("Quitting movie mover script.")
		running = False

log("Movie mover has quit")