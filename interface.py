#!/usr/local/bin/python

#############################################################################################
# PANDORA UNCHAINED INTERFACE by jfktrey
# release 1, 2013-5-18
#
# A command-line interface for using the Pandora Unchained library
#############################################################################################

import os, sys, subprocess, getpass

import PandoraUnchained
from terminalSize import getTerminalSize

## DEFINITIONS AND INITIALIZATIONS ##########################################################

RELEASE			= '1'
TERMINAL_WIDTH	= getTerminalSize()[0]
DOWNLOAD_TEXTS	= ['both your bookmarks and your likes.', 'your bookmarks only.', 'your likes only.']
TEXT_FILENAME	= 'songs.txt'
CSV_FILENAME	= 'songs.csv'

data		= None
email		= None
password	= None
download	= None
songList	= None

def printCentered (text):
	offset = (TERMINAL_WIDTH - len(text)) / 2
	print ' '*offset, text

def loginPrompt ():
	global data, email, password
	email		=       raw_input('                email: ')
	password	= getpass.getpass(' password (invisible): ')
	print
	print 'Logging in...'
	data = PandoraUnchained.PandoraUnchained(email, password)
	if (data.webname == 'login.vm'):
		print 'Error: invalid username/password pair. Try again.'
		loginPrompt()

def downloadPrompt ():
	global download
	download = raw_input('Enter the corresponding number: ')
	if not (download in ['1','2','3']):
		print 'Error: invalid code. Try again.'
		downloadPrompt()
	else:
		download = int(download)

def downloadByCode (code):
	global songList
	songList = []
	if (code < 3):
		sys.stdout.write('Downloading bookmarks')
		sys.stdout.flush()
		bookmarksList = data.getBookmarks(lambda bookmarkCount: updateProgress(bookmarkCount, 'bookmarks'))
		print ' Finished bookmarks, ' + str(len(bookmarksList)) + ' bookmarks downloaded. (some may be duplicates)\n'
		songList += bookmarksList
	if (code != 2):
		sys.stdout.write('Downloading likes')
		sys.stdout.flush()
		likesList = data.getLikes(lambda likeCount, thumbCount: updateProgress(noneSafeAddition(likeCount, thumbCount), 'likes'))
		print ' Finished likes, ' + str(len(likesList)) + ' likes downloaded. (some may be duplicates)'
		songList += likesList
	print
	sys.stdout.write('Removing duplicate songs...  ')
	sys.stdout.flush()
	songList = PandoraUnchained.makeSongListNoDuplicates(songList)

def noneSafeAddition (x, y):
	if (x == None) or (y == None):
		return None
	else:
		return x + y

def updateProgress (count, bookmarksOrLikes):
	if (count != None):
		sys.stdout.write('.')
		sys.stdout.flush()

def saveSongs ():
	global songList
	fileHandle = open(TEXT_FILENAME, 'w')
	fileHandle.write(PandoraUnchained.textFromSongList(songList))
	fileHandle.close()

	fileHandle = open(CSV_FILENAME, 'w')
	fileHandle.write(PandoraUnchained.csvFromSongList(songList))
	fileHandle.close()

def openFileBrowser (d):
	if sys.platform == 'win32':
		subprocess.Popen(['start', d], shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		print 'Done!'

	elif sys.platform == 'darwin':
		subprocess.Popen(['open', d], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		print 'Done!'

	else:
		try:
			subprocess.Popen(['xdg-open', d], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			print 'Done!'
		except:
			print 'Couldn\'t open your file, I can\'t figure out how to with your system. Sorry!'
			print 'You know where it is, though.'

## PROCEDURE ################################################################################

os.system(['clear','cls'][os.name == 'nt'])

printCentered('PANDORA UNCHAINED')
printCentered('release ' + RELEASE)
printCentered('by Trey Keown (jfktrey)')
print
print 'Pandora Unchained is a library that connects to Pandora Internet Radio and retrieves a list of your bookmarks and likes for you.'
print
print
print 'First, log into Pandora.'
loginPrompt()
print 'Success!'
print
print 'What do you want to download?'
print '  1: Bookmarks and Likes'
print '  2: Bookmarks only'
print '  3: Likes only'
print
downloadPrompt()
print 'Downloading ' + DOWNLOAD_TEXTS[download-1]
print
print 'You\'ll find your songs in the file ' + os.path.join(os.getcwd(), TEXT_FILENAME)
print 'That should be in the same place where you ran this program.'
print
print 'There is also a file called ' + CSV_FILENAME + ' that you can open in a program like Excel.'
print 'It already has the artist and title separated into separate columns for you.'
print
downloadByCode(download)
saveSongs()
print 'Done!'
sys.stdout.write('Opening your song list...    ')
sys.stdout.flush()
openFileBrowser(os.path.join(os.getcwd(), TEXT_FILENAME))
raw_input('Press enter to exit...')
print