#!/usr/bin/python3

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
	__gitBinary = ""
	__cacheFile = ""
	__data = None


	def __init__(self, path, remote = "origin", debug = False, gitBinary = "git"):
		self.__remote = remote
		self.__debug = debug
		self.__gitBinary = gitBinary

		self.__path = self.__findGitDirectory(path)

		if self.__path:
			self.__project = self.__getProjectName(self.__path)
			self.__cacheFile = os.path.expanduser('~') + '/.gitcache/' + self.__project + '_new'
			self.__data = self.__getCachedGitData()


	def __repr__(self):
		return 'GitStatus: project={project} expires={expires} cache={cache}'.format(
			project=self.__project, expires=self.__data.expires,
			cache=[self.__data.index, self.__data.head, self.__data.fetchHead, self.__data.status])


	def __findGitDirectory(self, path):
		while path != "/" and not os.path.isdir(path + '/.git'):
			path = os.path.dirname(path)

		if not path == "/":
			return path
		else:
			return None


	def __getProjectName(self, gitPath):
		return os.path.basename(gitPath)


	def get(self):
		if not self.__path:
			return ""

		data = self.__getRefreshedGitData()

		if not self.__data:
			self.__print("Data is empty, set cache dirty.")
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

		self.__print("expired: " + str(expired) + " indexDirty: " + str(indexDirty) + " headDirty: " + str(headDirty) + " fetchHeadDirty: " + str(fetchHeadDirty))
		return True if expired or indexDirty or headDirty or fetchHeadDirty else False


	def __getCachedGitData(self):
		cache = self.__readCacheFile()
		cache = list(map(lambda c: c.strip(), cache))

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
		indexFile = self.__path + '/.git/index'

		if os.path.isfile(indexFile):
			return int(os.path.getmtime(indexFile))
		else:
			return 0


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
			print("HeadFile: Failed to open file for reading (HEAD).")

		return headFile


	def __getGitHead(self, headFile):
		headCommit = ""

		if os.path.isfile(headFile):
			try:
				with open(headFile) as f:
					headCommit = f.read().strip()
				f.close()
			except IOError:
				print("Head: Failed to open file for reading (" + headFile + ").")
		else:
			# It is possible that the HeadFile does not exist.
			self.__print("HeadFile does not exist yet: " + headFile)

		return headCommit


	def __getGitFetchHead(self, headFile):
		fetchHeadCommit = ""
		headBranch = headFile.split('/.git/refs/heads/')
		headBranch = headBranch[-1]
		fetchHeadFile = self.__path + '/.git/refs/remotes/' + self.__remote + '/' + headBranch
		self.__print("FetchHead file is: " + fetchHeadFile)

		if os.path.isfile(fetchHeadFile):
			try:
				with open(fetchHeadFile) as f:
					fetchHeadCommit = f.read().strip()
				f.close()
			except IOError:
				print("FetchHead: Failed to open file for reading (" + fetchHeadFile + ").")
		else:
			# If repository is cloned but no fetch is called yet, FetchHead does not exist.
			self.__print("FetchHeadFile does not exist yet: " + fetchHeadFile)

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
			print('Failed to write file: {}'.format(self.__cacheFile))


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
		result = subprocess.check_output([self.__gitBinary, "--work-tree=" + self.__path, "status", "-sb"])
		output = result.splitlines()
		status = output.pop(0).decode(encoding='UTF-8')

		changed = 0
		new= 0
		added = 0
		modified = 0
		deleted = 0
		moved = 0

		for line in output:
			line = line.strip().decode(encoding='UTF-8')

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
		status += self.__formatStatus("?", new)
		status += self.__formatStatus("A", added)
		status += self.__formatStatus("M", modified)
		status += self.__formatStatus("D", deleted)
		status += self.__formatStatus("R", moved)

		return status


	def __formatStatus(self, status, count):
		if count > 0:
			return " " + status + ":" + str(count)
		else:
			return ""


	def __readCacheFile(self):
		lines = []

		if os.path.isfile(self.__cacheFile):
			try:
				with open(self.__cacheFile, 'r') as f:
					lines = f.readlines()
				f.close()
			except IOError:
				print('Failed to open file for reading: {}'.format(self.__cacheFile))
		else:
			# If the cache does not exist, it will be created later.
			self.__print('File does not exist: {}'.format(self.__cacheFile))

		return lines 


	def __print(self, string):
		if self.__debug:
			print(string)


GitStatus = GitStatus(os.getcwd(), debug=False, gitBinary="/usr/bin/git")
print(GitStatus.get())
