import os

from comic import Comic


class Series:
    def __init__(self, location):
        self.contains = []
        self.thumbnail = None
        self.file = location
        print("Initializing " + location)
        for file in sorted(os.listdir(location)):
            print(file)
            extension = (file.split(".")[-1])
            if extension in ["cbr", "cbz", "rar", "zip"]:
                issue = Comic(location, file)
                self.contains.append(issue)
        self.thumbnail = self.contains[0].thumbnail
        print("set series thumbnail to that of " + self.contains[0].file)
        print()


class Collection:

    def __init__(self, location):
        self.contains = []
        print("Creating new collection")
        for item in sorted(os.listdir(location)):
            if os.path.isdir(location + "/" + item):
                self.contains.append(Series(location + "/" + item))
            else:
                print("Adding " + item + " To collection")
                self.contains.append(Comic(location, item))
