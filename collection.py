import os

import preferences
from comic import comic

class comiclist():
	def __init__(self, name,  comicsin = []):
		self.name = name
		for item in comicsin:
			if type(item) != type(comic()):
				raise Exception("Comiclist object must cointain only comics")
		self.contained_comics = comicsin

	def comicswithchar(self, character):
		pass
	def sortcomics(self): #sorts comics by series and publication date:
		self.contained_comics.sort(key =lambda comic: comic.issue)
		self.contained_comics.sort(key =lambda comic: comic.publication_date)
		self.contained_comics.sort(key =lambda comic: comic.series)

	def find_comic_files(directory, verbose=False):
		try:
			directory = directory.strip("'")
		except:
			pass
		print(directory)
		comics = []
		walk = os.walk(directory)
		for directory in walk:
			if verbose == True:
				print("exploring directory" + directory[0])
			for filename in directory[2]:
				if filename.split(".")[-1] in preferences.allowed_extensions:
					comics.append(comic(filepath = directory[0] +"/" + filename))
		#print(comics)
		return comics



	def init_comics(self, verbose = False):
		for issue in self.contained_comics:
			if verbose:
				issue.get_info_from_filepath(verbose = True)
			else:
				issue.get_info_from_filepath()
		#remove all the comics that don't have issue numbers
		for issue in self.contained_comics:
			if issue.issue == -1:
				self.contained_comics.remove(issue)
			if verbose:
				#print("removed bad issue")
				pass
	def write_db(self):
		"""Writes all of info in the comic objects to sqlite database"""
		#create a new database file for this list
		for item in self: #for each comic that exists, write that to the mysql database
			pass
