import os, shutil, logging, urllib, time

## Config
dlDirectory = 'Download/'
movieDestination = 'Destination/'
minFileSize = 5000 ##1073741824 ## 1 gig
xbmcUrl = 'http://localhost:8080'
jsonRpcUrl = xbmcUrl + '/jsonrpc'
sleepSecs = 5 ## 360 ## 6 hours

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
	for root, dirs, files in os.walk(dlDirectory):
		for file in files:
			path = os.path.join(root, file)
			size = os.path.getsize(path)
			if (size > minFileSize):
				newpath = os.path.join(movieDestination, file)
				log("Renaming '" + path + "' to '" + newpath + "'")
				os.rename(path, newpath)
				postdata = '{"jsonrpc": "2.0", "method": "VideoLibrary.ScanForContent", "id": "1"}'
				log("Updating XBMC library.")
				respdata = urllib.urlopen(jsonRpcUrl, postdata).read()

	for root, dirs, files in os.walk(dlDirectory):
		if dirs != []:
			for dir in dirs:
				dirPath = os.path.join(root, dir)
				log("Removing directory '" + dirPath + "'")
				shutil.rmtree(dirPath)
	try:
		time.sleep(sleepSecs)
	except Exception, e:
		log("Quitting movie mover script.")
		running = False
	except KeyboardInterrupt, e:
		log("Quitting movie mover script.")
		running = False

log("Movie mover has quit")