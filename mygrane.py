#!/usr/bin/env python3

import os
import re
from datetime import date
import sqlite3

allowed_extensions = ['cbz', 'cbr', 'pdf']
database_dir = "../comics"

import comic

class comiclist():
	def __init__(self, name,  comicsin = []):
		self.name = name
		for item in comicsin:
			if type(item) != type(comic()):
				raise Exception("Comiclist object must cointain only comics")
		self.contained_comics = comicsin

	def comicswithchar(self, character):
		pass
	def sortcomics(self): #sorts comics by series and publication date
		self.contained_comics.sort(key =lambda comic: comic.publication_date)
		self.contained_comics.sort(key =lambda comic: comic.series)

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
	def write_db(self):
		"""Writes all of info in the comic objects to sqlite database"""
		#create a new database file for this list
		for item in self: #for each comic that exists, write that to the mysql database
			pass



comic_list = comiclist(comiclist.find_comic_files("/home/nsh/Documents/Comics"))
comic_list.init_comics()
def command_interpreter(input1, input2):
	global comic_list
	if input1 == "initdir":
		comic_list = comiclist(comiclist.find_comic_files(input2))
		comic_list.init_comics()
	elif input1 in ["listcomics", "ls", "lc", "list"]:
		for issue in comic_list.contained_comics:
			issue.printinfo()
	elif input1 == "sort":
		comic_list.sortcomics()
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
