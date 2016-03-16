import os
import preferences
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
                if preferences.preload_cover_images:
                    issue.set_thumbnail()
                self.contains.append(issue)
        self.contains[0].set_thumbnail()
        self.thumbnail = self.contains[0].thumbnail
        print("set series thumbnail to that of " + self.contains[0].file)
        print()

    def to_collection(self):
        return Collection(contains=self.contains)


class Collection:
    def __init__(self, location="", contains=[]):
        self.contains = []
        if location != "":
            print("Creating new collection")
            for item in sorted(os.listdir(location)):
                if os.path.isdir(location + "/" + item):
                    self.contains.append(Series(location + "/" + item))
                else:
                    print("Adding " + item + " To collection")
                    newcomic = Comic(location, item)
                    newcomic.set_thumbnail()
                    self.contains.append(newcomic)
        else:
            for item in contains:
                if not preferences.preload_cover_images:
                    print("Setting thumnail for " + item.file)
                    item.set_thumbnail()
                self.contains.append(item)
