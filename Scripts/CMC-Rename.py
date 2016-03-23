import os
walk = os.walk(".")
for directory in walk:
	for filename in directory[2]:
		print filename
		extension = filename.split(".")[-1]
		if extension == "cbz" or extension == "cbr":
			year = filename[:4]
			newname =  filename[7:-4] + " (" + year + ")" + "." + extension
			print newname
			os.system("mv '" + filename + "' '" + newname + "'")
