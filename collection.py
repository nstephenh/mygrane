import os
import preferences
from comic import Comic


class Series:
    def __init__(self, location="", name="", contents=[]):
        self.name = name
        self.issue = -1
        if contents != []:
            self.contains = contents
        else:
            self.contains = []
            print("Initializing " + location)
            for file in sorted(os.listdir(location)):
                print(file)
                extension = (file.split(".")[-1])
                if extension in ["cbr", "cbz", "rar", "zip"]:
                    issue = Comic(location, file)
                    if preferences.preload_cover_images:
                        issue.set_thumbnail()
                    self.contains.append(issue)
        self.file = self.contains[0].containing_directory
        if name == "":
            self.name = self.contains[0].title
        self.thumbnail = None
        print()

    def set_thumbnail(self):
        self.contains[0].set_thumbnail()
        self.thumbnail = self.contains[0].thumbnail
        print("set series thumbnail to that of " + self.contains[0].file)

    def to_collection(self):
        return Collection(contains=self.contains)

    def name_close_enough(self, theirs):
        if self.name == theirs:
            return True
        if self.name.lower == theirs.lower:
            return True
        return False

    def to_string(self, indent=False):
        output = ""
        for item in self.contains:
            if indent:
                output += '\t'
            output += (str(item) + '\n')
        return output


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
                    #newcomic.set_thumbnail()
                    self.contains.append(newcomic)
        else:
            for item in contains:
                if not preferences.preload_cover_images:
                    print("Setting thumnail for " + item.file)
                    item.set_thumbnail()
                self.contains.append(item)

    def sort(self, test=True):
        # presort self.contains to go by issue number
        self.contains.sort(key=lambda x: x.issue)

        temp_Contains = []
        # sort each comic into its own series
        for item in self.contains:
            if type(item) is Comic:
                index = 0
                found = False
                while index < len(temp_Contains):
                    # if the issue  we are looking at has a name close to the new comic
                    # and the publishing year is the same or the next year
                    # and the issue number is the next issue
                    # then append the issue to the
                    print(item.title + '\t' + str(temp_Contains[index].name_close_enough(item.title)) + '\t'
                          + str((temp_Contains[index].contains[-1].pubyear - item.pubyear) in [0, 1]) + '\t'
                          + str((temp_Contains[index].contains[-1].issue - item.issue) == -1))
                    if temp_Contains[index].name_close_enough(item.title) \
                            and (temp_Contains[index].contains[-1].pubyear - item.pubyear) in [0, 1] \
                            and (temp_Contains[index].contains[-1].issue - item.issue) == -1:
                        temp_Contains[index].contains.append(item)
                        print("Added " + item.title + " " + str(item.issue) + " to " + temp_Contains[index].name)
                        found = True
                    index += 1
                if not found:
                    # If there is no existing series, create a new one
                    print("Created new series for " + item.title)
                    temp_Contains.append(Series(name=item.title, contents=[item]))
            else:
                temp_Contains.append(item)
        # ToDo (Maybe): If series only contains one item, make it a comic object
        self.contains = temp_Contains

    def __str__(self):
        output = ""
        for item in self.contains:
            switch = type(item)
            if switch is Comic:
                output += (str(item) + '\n')
            elif switch is Series:
                output += item.name + '\n'
                output += item.to_string(indent=True)
        return output
