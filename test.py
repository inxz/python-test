#!/usr/bin/python

import os.path
import datetime

class GitStatus:

	__project = ""
	__path = ""
	__cacheFile = ""

	__cacheExpires = 0
	__cacheIndex = ""
	__cacheHead = ""
	__cacheFetchHead = ""
	__cacheStatus = ""

	__newExpires = 0
	__newIndex = ""
	__newHead = ""
	__newFetchHead = ""
	__newStatus = ""


	def __init__(self, project, path):
		self.__project = project
		self.__path = path
		self.__cacheFile = os.path.expanduser('~') + '/.gitcache/' + self.__project

		cache = self.__readCacheFile()
		cache = map(lambda c: c.strip(), cache)

		self.__cacheExpires = os.path.getmtime(self.__cacheFile)
		self.__cacheIndex = cache[0]
		# self.__cacheHead = cache[1]
		# self.__cacheFetchHead = cache[2]
		self.__cacheStatus = cache[3] 

		self.__newExpires = datetime.datetime.now().time()
		self.__newIndex = str(os.path.getmtime(self.__path + '/.git/index'))


	def __repr__(self):
		return 'GitStatus: project={project} expires={expires} cache={cache}'.format(
			project=self.__project, expires=self.__cacheExpires,
			cache=[self.__cacheIndex, self.__cacheHead, self.__cacheFetchHead, self.__cacheStatus])


	def writeCacheFile(self):
		try:
			with open(self.__cacheFile + '_new', 'w') as f:
				f.write(self.__newIndex + '\n')
				f.write(self.__newHead + '\n')
				f.write(self.__newFetchHead + '\n')
				f.write(self.__newStatus)
			f.close()
		except IOError:
			print 'Failed to write file: {}'.format(self.__cacheFile)


	def isCacheDirty(self):
		expired = self.isCacheExpired()
		indexDirty = self.__isIndexDirty()
		return True if expired or indexDirty else False


	def isCacheExpired(self):
		return True if self.__newExpires != self.__cacheExpires else False


	def __isIndexDirty(self):
		return True if self.__newIndex != self.__cacheIndex else False


	def __readCacheFile(self):
		lines = []

		if os.path.isfile(self.__cacheFile) :
			try:
				with open(self.__cacheFile, 'r') as f:
					lines = f.readlines()
				f.close()
			except IOError:
				print 'Failed to open file for reading: {}'.format(self.__cacheFile)
		else:
			print 'File does not exist: {}'.format(self.__cacheFile)

		return lines 


myFile = '/cygdrive/s/git-hub/inxz/dotfiles'
GitStatus = GitStatus('dotfiles', myFile)
print GitStatus
print GitStatus.isCacheDirty()
GitStatus.writeCacheFile()
