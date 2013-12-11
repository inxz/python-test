#!/usr/bin/python

import os.path
import time
import subprocess


class GitData:

	expires = 0
	index = ""
	head = ""
	fetchHead = ""
	status = ""


	def __init__(self, expires, index, head, fetchHead, status):
		self.expires = expires
		self.index = index
		self.head = head
		self.fetchHead = fetchHead
		self.status = status


class GitStatus:

	__project = ""
	__path = ""
	__remote = ""
	__debug = False
	__cacheFile = ""
	__data = None


	def __init__(self, project, path, remote = "origin", debug = False):
		self.__project = project
		self.__path = path
		self.__remote = remote
		self.__debug = debug
		self.__cacheFile = os.path.expanduser('~') + '/.gitcache/' + self.__project + '_new'

		self.__data = self.__getCachedGitData()


	def __repr__(self):
		return 'GitStatus: project={project} expires={expires} cache={cache}'.format(
			project=self.__project, expires=self.__data.expires,
			cache=[self.__data.index, self.__data.head, self.__data.fetchHead, self.__data.status])


	def get(self):
		data = self.__getRefreshedGitData()

		if not self.__data:
			cacheDirty = True
		else:
			cacheDirty = self.isCacheDirty(data)

		if cacheDirty:
			self.__print("Cache is dirty, updating git status and writing cache file.")
			gitStatus = self.__getGitStatus()
			data.status = gitStatus
			self.__data = data
			self.writeCacheFile(data)
			self.__data.status = "'" + self.__data.status
		else:
			self.__print("Cache is up2date, returning cached status.")

		return self.__data.status


	def isCacheDirty(self, data):
		expired = self.__isCacheExpired(data)
		indexDirty = self.__isIndexDirty(data)
		headDirty = self.__isHeadDirty(data)
		fetchHeadDirty = self.__isFetchHeadDirty(data)

		return True if expired or indexDirty or headDirty or fetchHeadDirty else False


	def __getCachedGitData(self):
		cache = self.__readCacheFile()
		cache = map(lambda c: c.strip(), cache)

		if len(cache) > 0:
			expires = int(os.path.getmtime(self.__cacheFile))
			index = int(cache[0])
			head = cache[1]
			fetchHead = cache[2]
			status = cache[3]

			return GitData(expires, index, head, fetchHead, status)
		else:
			self.__print("Can not read GitData from cache file.")
			return None


	def __getRefreshedGitData(self):
		expires = self.__getNewExpires()
		index = self.__getGitIndex()
		headFile = self.__getGitHeadFile()
		head = self.__getGitHead(headFile)
		fetchHead = self.__getGitFetchHead(headFile)

		return GitData(expires, index, head, fetchHead, None)


	def __getNewExpires(self):
		return time.time()


	def __getGitIndex(self):
		return int(os.path.getmtime(self.__path + '/.git/index'))


	def __getGitHeadFile(self):
		head = ""
		headFile = ""

		try:
			with open(self.__path + '/.git/HEAD') as f:
				head = f.read().strip()
			f.close()
			head = head.split()

			if head[0] == "ref:":
				head = head[1]
			else:
				head = head[0]

			headFile = self.__path + '/.git/' + head
		except IOError:
			print "Failed to open file for reading."

		return headFile


	def __getGitHead(self, headFile):
		headCommit = ""

		try:
			with open(headFile) as f:
				headCommit = f.read().strip()
			f.close()
		except IOError:
			print "Failed to open file for reading."

		return headCommit


	def __getGitFetchHead(self, headFile):
		fetchHeadCommit = ""
		headBranch = headFile.split('/')
		headBranch = headBranch[-1]
		fetchHeadFile = self.__path + '/.git/refs/remotes/' + self.__remote + '/' + headBranch
		self.__print("FetchHead file is: " + fetchHeadFile)

		try:
			with open(fetchHeadFile) as f:
				fetchHeadCommit = f.read().strip()
			f.close()
		except IOError:
			print "Failed to open file for reading."

		return fetchHeadCommit


	def writeCacheFile(self, data):
		try:
			with open(self.__cacheFile, 'w') as f:
				f.write(str(data.index) + '\n')
				f.write(data.head + '\n')
				f.write(data.fetchHead + '\n')
				f.write(data.status)
			f.close()
		except IOError:
			print 'Failed to write file: {}'.format(self.__cacheFile)


	def __isCacheExpired(self, data):
		difference = data.expires - 60 - self.__data.expires
		return True if difference > 0 else False


	def __isIndexDirty(self, data):
		return True if data.index != self.__data.index else False


	def __isHeadDirty(self, data):
		return True if data.head != self.__data.head else False


	def __isFetchHeadDirty(self, data):
		return True if data.fetchHead != self.__data.fetchHead else False


	def __getGitStatus(self):
		result = subprocess.check_output(["git", "status", "-sb"])
		output = result.split("\n")
		status = output.pop(0)

		changed = 0
		new= 0
		added = 0
		modified = 0
		deleted = 0
		moved = 0

		for line in output:
			line = line.strip()

			if line == "":
				continue

			changed += 1

			if line.startswith("??"):
				new += 1
			elif line.startswith("A"):
				added += 1
			elif line.startswith("M"):
				modified += 1
			elif line.startswith("D"):
				deleted += 1
			elif line.startswith("R"):
				moved += 1

		status += " *:" + str(changed)

		if new > 0:
			status += " ?:" + str(new)

		if added > 0:
			status += " A:" + str(added)

		if modified > 0:
			status += " M:" + str(modified)

		if deleted > 0:
			status += " D:" + str(deleted)

		if moved > 0:
			status += " R:" + str(moved)

		return status


	def __readCacheFile(self):
		lines = []

		if os.path.isfile(self.__cacheFile):
			try:
				with open(self.__cacheFile, 'r') as f:
					lines = f.readlines()
				f.close()
			except IOError:
				print 'Failed to open file for reading: {}'.format(self.__cacheFile)
		else:
			print 'File does not exist: {}'.format(self.__cacheFile)

		return lines 


	def __print(self, string):
		if self.__debug:
			print string


myFile = '/cygdrive/s/git//hub/inxz/dotfiles'
GitStatus = GitStatus('dotfiles', myFile)
print GitStatus.get()
