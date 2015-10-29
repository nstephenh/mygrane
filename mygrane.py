
import os
import re
from datetime import date

allowed_extensions = ['cbz', 'cbr', 'pdf']

class comic():
	def __init__(self, issue= -1, authors = [], franchise="", series="", publication_date=date.min, date_accuracy = "null", publisher="", filepath = ""):
		self.issue = issue
		self.series = series
		self.authors = authors
		self.franchise = franchise
		self.publisher = publisher
		self.publication_date = publication_date
		self.date_accuracy = date_accuracy
		self.filepath = filepath
		self.characters = []
	def getfranchise(self):
		return self.franchise
	
	def addcharacter(self, character):
		self.characters.append(character)

	def get_info_from_filepath(self):
		"""
		Returns the following information from the filename in the following formats
		issue - 1-3 digits followed by a space or .
		series - the string in the filename before the number
		formats:
			nem
			cmc
		"""
		infoformat = "unknown"
		filename = self.filepath.split("/")[-1] # Gives us the raw filename
		#print("Extracting info from " +self.filepath)
		# get the publication date name from the filename
		yearregex = re.compile("[1-2][90]\d\d")
		monthregexcmc = re.compile("[1-2][90]\d\d([01][0-9])")
		monthregexnem = re.compile("([01][1-9])-[0-3][0-9]-[1-2][90]\d\d")
		dayregex = re.compile("[01][1-9]-([0-3][0-9])-[1-2][90]\d\d")
		try:	
			year = int(yearregex.findall(self.filepath)[-1]) # returns the last date found in the filepath
			self.date_accuracy = "year"
		except Exception as e:
			#print(e)
			year = 1
			self.date_accuracy = "null"
		try:
			month = int(monthregexcmc.search(self.filepath).group(1))
			infoformat = "cmc"
			self.date_accuracy = "month"
		except Exception as e:
			#print(e)
			try:
				month = int(monthregexnem.search(self.filepath).group(1))
				infoformat = "nem"
				self.date_accuracy = "month"
			except Exception:
				month = 1
		try:
			day = int(dayregex.search(self.filepath).group(1))
			self.date_accuracy = "day"
		except Exception as e:
			#print(e)
			day = 1
		#print(str(year) + str(month) + str(day))
		self.publication_date = date(year, month, day) # Set the publication date to the found date
		
		try: #Get the issue number from the filename
			issueregex = re.compile("(\d{1,3})[\.| |\(]")
			self.issue = int(issueregex.findall(filename)[-1])
		except Exception as e:
			print("No issue number found due to: " + str(e))

		try: #Get the series name from the filename
			beforeparen = filename.split("(")[0].strip()
			nonumber = beforeparen.split(str(self.issue))[0].strip('0').strip()
			#print(infoformat)
			if infoformat != "cmc":
				self.series = nonumber
			else:
				self.series = nonumber[7:]
		except Exception as e:
			print("Series Name not found due to: " + str(e))
			pass
		
		
	def printinfo(self):
		print(self.series +" "+ str(self.issue)+ " (" + str(self.publication_date)+") accurate to the " + self.date_accuracy)

class comiclist():
	def __init__(self, comicsin):
		self.contained_comics = comicsin
	def comicswithchar(character, sortkey = "publication_date"):
		pass

	def find_comic_files(directory):
		try:
			directory = directory.strip("'")
		except:
			pass
		comics = []
		walk = os.walk(directory)
		for directory in walk:
			for filename in directory[2]:
				if filename.split(".")[-1] in allowed_extensions:
					comics.append(comic(filepath = directory[0] +"/" + filename))
		return comics

	def init_comics(self):
		for issue in self.contained_comics:
			issue.get_info_from_filepath()


def command_interpreter(input1, input2):
	global comic_list
	if input1 == "initdir": 
		comic_list = comiclist(comiclist.find_comic_files(input2))
		comic_list.init_comics()
	elif input1 == "listcomics":
		for issue in comic_list.contained_comics:
			issue.printinfo()
	elif input1 == "exit" or input1 == 'q':
		exit()
	
while True:
	textin = input("Enter Command:")
	input1 = textin.split()[0]
	try:
		input2 = textin.split()[1]
	except:
		input2 = ""
	command_interpreter(input1, input2)
	
