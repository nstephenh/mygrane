
import os
import re
from datetime import date

allowed_extensions = ['cbz', 'cbr', 'pdf']

class comic():
	def __init__(self, issue= -1, franchise="", series="", publication_date=date.min, publisher="", filepath = ""):
		self.issue = issue
		self.series = series
		self.franchise = franchise
		self.publisher = publisher
		self.publication_date = publication_date
		self.filepath = filepath
		self.characters = []
	def getfranchise(self):
		return self.franchise
	def addcharacter(self, character):
		self.characters.append(character)

def comicswithchar(character, sortkey = "publication_date"):
	pass

def find_comic_files(directory):
	comics = []
	walk = os.walk(directory)
	for directory in walk:
		for filename in directory[2]:
			if filename.split(".")[-1] in allowed_extensions:
				comics.append(comic(filepath = directory[0] +"/" + filename))
	return comics
def get_info_from_filepath(filepath):
	noextension = filepath.split(".")[-2] # Remove the extension from the filepath, as we know 
	filename = noextension.split("/")[-1] # Gives us the raw filename
	return str(re.match("", filename).group(0)) # Find the issue number

	
	

def init_comics(comics):
	for issue in comics:
		print(get_info_from_filepath(issue.filepath))	
	return comics

init_comics(find_comic_files('/home/nsh/Documents/Comics'))
