#!/usr/local/bin/python

#############################################################################################
# PANDORA UNCHAINED by jfktrey
# release 1, 2013-5-18
#
# Free your Pandora bookmarks and likes for use on other platforms.
#############################################################################################

import sys, os, json, csv, io, StringIO
from collections import OrderedDict
from string import Template

import twill.commands as Browser 	# These twill libraries are modified. See commands.js for more details.
import twill.browser as _browser
from twill.BeautifulSoup3 import BeautifulSoup

LOGFILE					= open('log.txt', 'w')
Browser.OUT				= LOGFILE
_browser.OUT			= LOGFILE

PANDORA_LOGIN_URL		= 'http://www.pandora.com/login.vm'
PANDORA_WEBNAME_URL		= Template('http://feeds.pandora.com/services/ajax/?method=authenticate.emailToWebname&email=${email}')
PANDORA_BOOKMARKS_URL	= Template('http://www.pandora.com/content/bookmarked_tracks?trackStartIndex=${trackstart}&webname=${webname}')							#returns 5 bookmarks at a time
PANDORA_LIKES_COUNT_URL	= Template('http://www.pandora.com/content/likes?webname=${webname}')
PANDORA_LIKES_URL 		= Template('http://www.pandora.com/content/tracklikes?likeStartIndex=${likestart}&thumbStartIndex=${thumbstart}&webname=${webname}')	#returns 5 or 10 bookmarks at a time (...???)
PANDORA_STATIONS_URL	= Template('http://www.pandora.com/content/stations?startIndex=${start}&webname=${webname}')											#returns all stations

# The information that comes about a user's profile from v35, while useful (number of bookmarks, number of likes, number of stations), is encrypted.
# Even the request's POST data is encrypted with Blowfish. I can't just insert values into the request because it's encrypted. Would be possible through much more work or a full-blown headless browser like PhantomJS.

class PandoraUnchained:
	def __init__ (self, email, password):
		Browser.go(PANDORA_LOGIN_URL)
		Browser.formvalue(1, 'login_username', email)
		Browser.formvalue(1, 'login_password', password)
		Browser.submit()

		self.webname = Browser.info().split('/').pop()

	def getNumberOfLikes (self):
		url = PANDORA_LIKES_COUNT_URL.substitute(webname = self.webname)
		Browser.go(url)

		soup = BeautifulSoup(Browser.show())
		songsDiv = soup.find('div', {'id': 'songs'})
		numberSpan = songsDiv.find('span', {'class': 'section_count'})

		return int(numberSpan.text.strip('()'))

	def getBookmarks (self, currentTrackCallback):
		lastRequestedTrackIndex = 0 	# the number of the first track that was requested in the previous set of bookmarks
		newBookmarksCount = 0			# the number of new bookmarks in this request
		bookmarks = []
		
		while self._returnedFullPageOfBookmarks(lastRequestedTrackIndex, newBookmarksCount):
			newTrackIndex = lastRequestedTrackIndex + newBookmarksCount
			newBookmarks = self._requestBookmarks(newTrackIndex)
			lastRequestedTrackIndex = newTrackIndex

			bookmarks += newBookmarks 				# adding in the actual song titles and artists
			newBookmarksCount = len(newBookmarks)	# the number of new bookmarks in this request

			currentTrackCallback(lastRequestedTrackIndex)

		return bookmarks

	def _requestBookmarks (self, startingTrack):
		url = PANDORA_BOOKMARKS_URL.substitute(trackstart = startingTrack, webname = self.webname)
		Browser.go(url)

		return self._songHtmlToList(Browser.show())

	def _returnedFullPageOfBookmarks (self, startingTrack, numberOfBookmarks):
		if  (startingTrack == numberOfBookmarks == 0):
			return True
		elif (startingTrack <= 5) and (numberOfBookmarks == 5):
			return True
		elif (startingTrack > 5) and (numberOfBookmarks == 10):
			return True
		else:
			return False

	def getLikes (self, currentTrackCallback):
		likeIndex = 0
		thumbIndex = 0
		newLikesCount = 0

		likes = []
		
		while (likeIndex != None) and (thumbIndex != None):
			(newLikes, likeIndex, thumbIndex) = self._requestLikes(likeIndex, thumbIndex)

			currentTrackCallback(likeIndex, thumbIndex)

			likes += newLikes
			newLikesCount = len(newLikes)

		return likes

	def _requestLikes (self, startingLike, startingThumb):
		url = PANDORA_LIKES_URL.substitute(webname = self.webname, likestart = startingLike, thumbstart = startingThumb)
		Browser.go(url)

		likesList = self._songHtmlToList(Browser.show())

		soup = BeautifulSoup(Browser.show())
		nextInfoElement = soup.find('div', {'class': 'show_more tracklike'})

		nextStartingLike = self._attributeNumberValueOrZero(nextInfoElement, 'data-nextlikestartindex')
		nextStartingThumb = self._attributeNumberValueOrZero(nextInfoElement, 'data-nextthumbstartindex')

		return (likesList, nextStartingLike, nextStartingThumb)

	def _songHtmlToList (self, html):
		songList = []

		soup = BeautifulSoup(Browser.show())
		songs = soup.findAll('div', {'class': 'infobox-body'})
		for song in songs:
			links = song.findAll('a')
			title = links[0].text
			artist = links[1].text
			songList.append([title, artist])

		return songList

	def _attributeNumberValueOrZero (self, element, attribute):
		try:
			return int(element[attribute])
		except KeyError:
			return 0
		except TypeError:
			return None

	def close (self):
		LOGFILE.close()

#############################################################################################

def textFromSongList (songList):
	songText = ''

	for song in songList:
		songText += '%s by %s\n' %(song[0], song[1])

	return songText

def csvFromSongList (songList):
	songCsv		= StringIO.StringIO()
	songList	= [['title', 'artist']] + songList

	writer = csv.writer(songCsv, delimiter = '\t')

	for song in songList:
		writer.writerow(song)

	return songCsv.getvalue()

def makeSongListNoDuplicates (songList):
	cleanedSongList = []

	for song in songList:
	    if song not in cleanedSongList:
       		cleanedSongList.append(song)

	return cleanedSongList

def getWebnameFromEmail (self, email):
	url = PANDORA_WEBNAME_URL.substitute(email = email)
	Browser.go(url)

	responseJson = json.loads(Browser.show())
	return responseJson['result']['webname']