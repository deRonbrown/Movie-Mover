import os
import shutil
import logging
import urllib
from time import sleep, localtime, strftime
from Config import Config

try:
	os.remove('./messages.log')
except OSError as (errno, strerror):
	print "messages.log does not exits"

logger = logging.getLogger('Movie-Mover')
hdlr = logging.FileHandler('./messages.log')
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr)
logger.setLevel(logging.INFO)

def log(msg):
	logger.info(msg)
	time = strftime("%Y-%m-%d %H:%M:%S", localtime())
	print time + " [II]: " + msg

def logErr(msg):
	logger.error(msg)
	time = strftime("%Y-%m-%d %H:%M:%S", localtime())
	print time + " [EE]: " + msg

running = True
while running:
	update = False
	for root, dirs, files in os.walk(Config.DL_DIRECTORY):
		for file in files:
			path = os.path.join(root, file)
			size = os.path.getsize(path)
			if (size < Config.MIN_FILE_SIZE):
				log("Attempting to remove: '" + path + "'.")
				try:
					os.remove(path)
					log("Remove successful for: '" + path + "'.")
				except OSError as (errno, strerror):
					error = "Remove failed for: '" + path + "'. {0}: {1}"
					error.format(errno, strerror)
					logErr(error)
			else:	
				newpath = os.path.join(Config.MOVIE_DESTINATION, file)
				log("Found movie: " + file)
				log("Attempting to rename '" + path + "' to '" + newpath + "'.")
				try:
					os.rename(path, newpath)
					log("Rename successful: '" + path + "' to '" + newpath + "'")
					update = True
				except OSError as (errno, strerror):
					error = "Rename (move) failed. {0}: {1}".format(errno, strerror)
					logErr(error)
				
				notification = Config.XBMC_URL + "/xbmcCmds/xbmcHttp?command=ExecBuiltIn(Notification(" + file + ", Download Complete))"
				try:
					urllib.urlopen(notification).close()
				except IOError as (errno, strerror):
					error = "Failed to execute XBMC notification command. {0}: {1}".format(errno, strerror)
				
	if (update):
		updateLibrary = Config.XBMC_URL + "/xbmcCmds/xbmcHttp?command=ExecBuiltIn(UpdateLibrary(video, " + Config.MOVIE_DESTINATION + "))"
		try:
			urllib.urlopen(updateLibrary).close()
			update = False
		except IOError as (errno, strerror):
			error = "Failed to execute XBMC update library command. {0}: {1}".format(errno, strerror)
	
	for root, dirs, files in os.walk(Config.DL_DIRECTORY):
		for dir in dirs:
			dirPath = os.path.join(root, dir)
			if os.listdir(dirPath) == []:
				log("Attempting to remove empty directory: '" + dirPath + "'")
				try:
					shutil.rmtree(dirPath)
					log("Remove of directory succeeded: '" + dirPath + "'")
				except OSError as (errno, strerror):
					error = "Removing of directory failed. {0}: {1}".format(errno, strerror)
					logErr(error)
			else:
				log("Directory is not empty. Path: '" + dirPath + "'")

	try:
		sleep(Config.SLEEP_SECS)
	except Exception:
		running = False
	except KeyboardInterrupt:
		running = False