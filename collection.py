import os
import preferences
from comic import Comic
import re


class Series:
    def __init__(self, location="", name="", contents=[]):
        self.name = name
        self.issue = -1
        if contents != []:
            self.contains = contents
            self.file = self.contains[0].containing_directory
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
            self.file = location
        if name == "":
            self.name = self.contains[0].title
        self.pubyear = self.contains[0].pubyear
        self.thumbnail = None
        print()

    def set_thumbnail(self):
        self.contains[0].set_thumbnail()
        self.thumbnail = self.contains[0].thumbnail
        print("set series thumbnail to that of " + self.contains[0].file)

    def to_collection(self):
        return Collection(contains=self.contains)

    def name_close_enough(self, theirs):
        oursbase = self.name
        theirsbase = theirs
        if self.name == theirs:
            return True
        oursbase.lower
        theirsbase.lower
        if oursbase == theirsbase:
            return True
        oursbase = re.sub("[^0-9a-z]", "", oursbase)
        theirsbase = re.sub("[^0-9a-z]", "", theirsbase)
        if oursbase == theirsbase:
            # If the only difference is special characters and whitespace, then they are probably the same
            return True
        re.sub('and', "",  oursbase, flags=re.IGNORECASE)
        re.sub('and', "",  theirsbase, flags=re.IGNORECASE)
        if oursbase == theirsbase:
            # same as above but with provisions for the word and (since it is sometimes replaced with ampersand)
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
                    # print(item.title + '\t' + str(temp_Contains[index].name_close_enough(item.title)) + '\t'
                        # + str((temp_Contains[index].contains[-1].pubyear - item.pubyear) in [0, 1]) + '\t'
                        # + str((temp_Contains[index].contains[-1].issue - item.issue) == -1))
                    if temp_Contains[index].name_close_enough(item.title) \
                            and (item.pubyear - temp_Contains[index].contains[-1].pubyear) in [0, 1] \
                            and (item.issue - temp_Contains[index].contains[-1].issue) == 1:
                        if not test:
                            try:
                                olditemdir = item.containing_directory
                                item.title = temp_Contains[index].name
                                item.containing_directory += "/" + item.title + " (" + str(temp_Contains[index].pubyear) + ")/"
                                os.rename(olditemdir + item.file, item.containing_directory + item.file)
                            except os.error as e:
                                print("Error, comic already exists in directory or")
                                print(e)
                        temp_Contains[index].contains.append(item)
                        print("Added " + item.title + " " + str(item.issue) + " to " + temp_Contains[index].name)
                        found = True
                    index += 1
                if not found:
                    # If there is no existing series, create a new one
                    print("Created new series for " + item.title)
                    if not test:
                        try:

                            olditemdir = item.containing_directory
                            createddir = "/" + item.title + " (" + str(item.pubyear) + ")"
                            os.mkdir(olditemdir + createddir)
                            item.containing_directory += createddir + "/"
                            os.rename(olditemdir + item.file, item.containing_directory + item.file)
                            temp_Contains.append(Series(name=item.title,
                                                        location=item.containing_directory,  contents=[item]))
                        except os.error:
                            print("Directory already exists: " + item.title + " (" + str(item.pubyear) + ")")
                    else:
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
