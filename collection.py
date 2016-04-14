import os
import preferences
from comic import Comic
import re


class Series:
    def __init__(self, location="", name="", contents=[]):
        self.name = name
        self.title = name  # for compatability with comic objects
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
        oursbase = oursbase.lower()
        theirsbase = theirsbase.lower()
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
        self.location=location
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
                if self.location == "" and type(item) is Series:
                    self.location = self.contains[0].file

    def sort(self, test=True, allow_duplicates=False):
        # presort self.contains to go by issue number
        self.contains.sort(key=lambda x: x.issue)

        temp_Contains = []
        # sort each comic into its own series
        for item in self.contains:
            if type(item) is Comic:
                index = 0
                found = False
                while index < len(temp_Contains):
                    series = temp_Contains[index]
                    lastissue = series.contains[-1]
                    # if the issue  we are looking at has a name close to the new comic
                    # and the publishing year is the same or the next year
                    # and the issue number is the next issue
                    # then append the issue to the series
                    # if series.name_close_enough(item.title):
                        #print(item.title + '\t'
                            # + str((temp_Contains[index].contains[-1].pubyear - item.pubyear) in [0, 1]) + '\t'
                            # + str((temp_Contains[index].contains[-1].issue - item.issue) == -1))

                    # Special handling for 0 issues. If the last issue was a 0 issue then
                    # we check to see if the name is cloes enough
                    # and the next issue is a #1
                    # and the zero issue was published the year before at earliest
                    if lastissue.issue == 0 and series.name_close_enough(item.title) \
                            and (item.issue == 1) \
                            and (item.pubyear - lastissue.pubyear >= -1):
                        if not test:
                            try:
                                olditemdir = item.containing_directory + "/"
                                item.title = series.name
                                if series.pubyear != item.pubyear:
                                    pass
                                    # ToDo: move the series folder
                                    # series.pubyear = item.pubyear
                                item.containing_directory += "/" + item.title + " (" + str(series.pubyear) + ")/"
                                os.rename(olditemdir + item.file, item.containing_directory + item.file)
                            except os.error as e:
                                print("Error, comic already exists in directory or")
                                print(e)
                        series.contains.append(item)
                        print("Added " + item.title + " " + str(item.issue) + " to " + temp_Contains[index].name)
                        found = True

                    elif temp_Contains[index].name_close_enough(item.title) \
                            and (item.pubyear - lastissue.pubyear) in [0, 1] \
                            and ((0 < (item.issue - lastissue.issue) <= 1) \
                                 or (0 <= (item.issue - lastissue.issue) <= 1 \
                                 and allow_duplicates)):
                        if not test:
                            item.move_file(series=temp_Contains[index])
                        temp_Contains[index].contains.append(item)
                        print("Added " + item.title + " " + str(item.issue) + " to " + temp_Contains[index].name)
                        found = True
                    index += 1
                if not found:
                    # If there is no existing series, create a new one
                    print("Created new series for " + item.title)
                    if not test:
                        try:
                            olditemdir = item.containing_directory + "/"
                            createddir = "/" + item.title + " (" + str(item.pubyear) + ")" + "/"
                            item.move_file(olditemdir + createddir)
                            temp_Contains.append(Series(name=item.title,
                                                        location=item.containing_directory,  contents=[item]))
                        except os.error:
                            print("Directory already exists: " + item.title + " (" + str(item.pubyear) + ")")
                    else:
                        # ToDo: Add in the ability to update to existing series under certain circumstances
                        temp_Contains.append(Series(name=item.title, contents=[item]))

            else:
                temp_Contains.append(item)

        # If series only contains one item, make it a comic object
        index = 0
        for item in temp_Contains:
            if type(item) is Series and len(item.contains) == 1:

                if not test:
                    # Move the file out of empty the collection
                    single = item.contains[0]
                    print(single.containing_directory)
                    single.move_file(self.location)
                    temp_Contains[index] = single
            index += 1

        self.contains = temp_Contains
        self.contains.sort(key=lambda x: x.title)

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
