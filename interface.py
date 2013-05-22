#!/usr/local/bin/python

#############################################################################################
# PANDORA UNCHAINED INTERFACE by jfktrey
# release 2, 2013-5-21
#
# A command-line interface for using the Pandora Unchained library
#############################################################################################

import os, sys, getpass, textwrap

import PandoraUnchained
from terminalSize import getTerminalSize

## DEFINITIONS AND INITIALIZATIONS ##########################################################

RELEASE			= '2'
TERMINAL_WIDTH	= getTerminalSize()[0]
HORIZONTAL_RULE	= '-'*(TERMINAL_WIDTH - 1)
DOWNLOAD_TEXTS	= ['both your bookmarks and your likes.', 'your bookmarks only.', 'your likes only.']
TEXT_FILENAME	= 'songs.txt'
CSV_FILENAME	= 'songs.csv'

data		= None
email		= None
password	= None
download	= None
songList	= None

def printWrapped (text):
	print textwrap.fill(text, width = TERMINAL_WIDTH)

def printCentered (text):
	offset = (TERMINAL_WIDTH - len(text)) / 2
	print ' '*offset, text

def loginPrompt ():
	global data, email, password
	email		=       raw_input('                email: ')
	password	= getpass.getpass(' password (invisible): ')
	print
	sys.stdout.write('Logging in... ')
	sys.stdout.flush()
	data = PandoraUnchained.PandoraUnchained(email, password)
	if (data.webname == 'login.vm'):
		print 'Couldn\'t log in. Try again.'
		loginPrompt()

def downloadPrompt ():
	global download
	download = raw_input('Enter the corresponding number: ')
	if not (download in ['1','2','3']):
		printWrapped('Enter one of the corresponding numbers above (1, 2, or 3)')
		downloadPrompt()
	else:
		download = int(download)

def downloadByCode (code):
	global songList
	songList = []
	if (code < 3):
		bookmarksList = data.getBookmarks(lambda bookmarkCount: updateProgress(bookmarkCount, 'bookmarks'))
		print 'Done.'
		songList += bookmarksList
	if (code != 2):
		likesList = data.getLikes(lambda likeCount, thumbCount: updateProgress(noneSafeAddition(likeCount, thumbCount), 'likes'))
		print 'Done.'
		songList += likesList
	print
	sys.stdout.write('Removing duplicate songs... ')
	sys.stdout.flush()
	songList = PandoraUnchained.makeSongListNoDuplicates(songList)

def noneSafeAddition (x, y):
	if (x == None) or (y == None):
		return None
	else:
		return x + y

def updateProgress (count, bookmarksOrLikes):
	if (count != None):
		sys.stdout.write('\rDownloaded %d %s... ' %(count, bookmarksOrLikes))
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
		os.startfile(d)
		print 'Done.'

	elif sys.platform == 'darwin':
		subprocess.Popen(['open', d], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
		print 'Done.'

	else:
		try:
			subprocess.Popen(['xdg-open', d], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
			print 'Done.'
		except:
			print 'Couldn\'t open your file, I can\'t figure out how to with your system. Sorry!'
			print 'You know where it is, though.'

## PROCEDURE ################################################################################

os.system(['clear','cls'][os.name == 'nt'])

printCentered('PANDORA UNCHAINED')
printCentered('release ' + RELEASE)
printCentered('by Trey Keown (jfktrey)')
print
printWrapped('Pandora Unchained is a library that connects to Pandora Internet Radio and retrieves a list of your bookmarks and likes for you.')
print
print HORIZONTAL_RULE
print
print 'First, log into Pandora.'
loginPrompt()
print 'Success!'
print
print HORIZONTAL_RULE
print
print 'What do you want to download?'
print '  1: Bookmarks and Likes'
print '  2: Bookmarks only'
print '  3: Likes only'
print
downloadPrompt()
print
print HORIZONTAL_RULE
print
printWrapped('Downloading ' + DOWNLOAD_TEXTS[download-1])
print
printWrapped('You\'ll find your songs in the file:')
print '    ' + os.path.join(os.getcwd(), TEXT_FILENAME)
printWrapped('That should be in the same place where you ran this program.')
print
printWrapped('There\'s also a file called ' + CSV_FILENAME + ' that you can open in a program like Excel.')
printWrapped('It has the artist and title separated into different columns for you.')
print
print HORIZONTAL_RULE
print
downloadByCode(download)
saveSongs()
print 'Done.'
sys.stdout.write('Opening your song list... ')
sys.stdout.flush()
openFileBrowser(os.path.join(os.getcwd(), TEXT_FILENAME))
raw_input('Press enter to exit.')
print
data.close()