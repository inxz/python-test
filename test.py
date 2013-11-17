#!/usr/bin/python

import os.path

def gitModified(gitProject, gitPath):
	homeDir = getHomeDir()
	cacheResult = readLines(homeDir + '/.gitcache/' + gitProject)
	print cacheResult
	gitIndex = gitIndexModified(gitPath + '/.git/index')
	print gitIndex
	return True

def readCacheFile( path ):
	result = []
	

def gitIndexModified( myFile ):
	mtime = os.path.getmtime(myFile)
	return mtime


def readLines( myFile ):
	lines = []

	if os.path.isfile(myFile) :
		try:
			with open(myFile) as f:
				lines = f.readlines()
			f.close()
		except IOError:
			print 'Failed to open file for reading: {}'.format(myFile)
	else:
		print 'File does not exist: {}'.format(myFile)

	return lines 


def getHomeDir():
	return os.path.expanduser('~')


myFile = '/cygdrive/d/git-hub/dotfiles'
print gitModified('dotfiles', myFile)
