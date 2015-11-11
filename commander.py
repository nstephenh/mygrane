import collection
class cli():
	#comic_list = comiclist(comiclist.find_comic_files("/home/nsh/Documents/Comics"))
	#comic_list.init_comics()
	def command_interpreter(input1, input2):
		global comic_list
		if input1 == "initdir":
			if input2 != "":
				comic_list = collection.comiclist(collection.comiclist.find_comic_files(input2))
				comic_list.init_comics()
			else:
				print("initdir requires dir to init")
		elif input1 in ["listcomics", "ls", "lc", "list"]:
			for issue in comic_list.contained_comics:
				issue.printinfo()
		elif input1 == "sort":
			comic_list.sortcomics()
		elif input1 == "exit" or input1 == 'q':
			exit()

	def start_cli():
		while True:
			textin = input("Enter Command:")
			input1 = textin.split()[0]
			try:
				input2 = textin.split()[1]
			except:
				input2 = ""
			cli.command_interpreter(input1, input2)
