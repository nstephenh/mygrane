import os
import re

from mygrane import preferences
from mygrane.comic import Comic

plaintext = re.compile("[^0-9a-z]")
andpersand = re.compile('and', flags=re.IGNORECASE)

thereplace = re.compile('the', flags=re.IGNORECASE)


class Series:
    def __init__(self, location="", name="", contents=[]):
        self.name = name
        self.title = name  # for compatability with comic objects
        self.issue = -1
        self.contains = []
        # print(contents) # debug line
        if contents != []:
            self.contains = contents
            self.file = self.contains[0].containing_directory  # Should be absolute...
        else:
            self.contains = []
            print("Initializing " + location)
            for file in sorted(os.listdir(location)):
                print(file)
                extension = (file.split(".")[-1])
                if extension.lower() in ["cbr", "cbz", "rar", "zip", "pdf"]:
                    issue = Comic(location, file)
                    if preferences.preload_cover_images:
                        issue.set_thumbnail()
                    self.contains.append(issue)
            self.file = location
        # print(self.file) #Debug line
        if name == "":
            # print(self.file)
            print(self.contains)
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
        oursbase = plaintext.sub("", oursbase.lower())
        theirsbase = plaintext.sub("", theirsbase.lower())
        if oursbase == theirsbase:
            # If the only diference is special characters and whitespace, then they are probably the same
            return True
        oursbase = andpersand.sub("", oursbase)
        theirsbase = andpersand.sub("", theirsbase)
        theirsbase = thereplace.sub("", theirsbase)
        oursbase = thereplace.sub("", oursbase)
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
    def __init__(self, location="", contains=[], flatten=False):
        self.contains = []
        self.location = location + "/"
        if location != "":
            print("Creating new collection")
            for item in sorted(os.listdir(location)):
                sublocation = location + "/" + item
                if os.path.isdir(sublocation):
                    # print(item)
                    if flatten == False:
                        self.contains.append(Series(sublocation))
                    else:
                        # If flatten is true then we want to cycle through each item
                        for subitem in sorted(os.listdir(sublocation + "/")):
                            self.contains.append(Comic(sublocation + "/", subitem))
                else:
                    try:
                        item.encode("UTF-8")
                        print("Adding " + item + " To collection")
                        newcomic = Comic(location, item)
                        # newcomic.set_thumbnail()
                        self.contains.append(newcomic)
                    except UnicodeEncodeError as ude:
                        print("Error adding item: " + sublocation.encode('utf-8', 'ignore').decode('utf-8'))

        else:
            for item in contains:
                if not preferences.preload_cover_images:
                    print("Setting thumnail for " + item.file)
                    item.set_thumbnail()
                self.contains.append(item)
                if self.location == "" and type(item) is Series:
                    self.location = self.contains[0].file

    def sort(self, test=True, allow_duplicates="False"):
        """

        :param test:
        :param allow_duplicates: "true" "false" or "delete". Delete will keep the copy with the highest filesize
        :return:
        """
        temp_Contains = []  # This is what we will return
        sortme = []  # This is what we use as a temporary container.
        special_second = []  # issues that might have come out after issue 1 go here. Any issue number less than 1

        # The following handles comics with no issue number by skipping them for the sort
        for item in self.contains:
            if type(item) is Comic:
                if item.issueNum is None:
                    # Trade Paperback or other item, has no issue number
                    temp_Contains.append(item)
                elif item.issueNum < 1:
                    # 0 issue or 0.1 issue, will go through on secondary pass
                    special_second.append(item)
                else:
                    # regular issues
                    sortme.append(item)
            else:
                # Series Objects
                temp_Contains.append(item)

        # TODO: Make issue 1 come before issue 1.MU, etc....

        # presort sort to go by issue number
        sortme.sort(key=lambda x: x.issueStr)  # hopefully fixes above todo^
        sortme.sort(key=lambda x: x.issueNum)
        special_second.sort(key=lambda x: x.issueNum)

        # sort each comic into its own series
        for item in sortme:
            # removed type(comic) check from here since we're doing that earlier again
            index = 0
            found = False
            while index < len(temp_Contains):
                series = temp_Contains[index]
                if type(series) is Series:
                    lastissue = series.contains[-1]
                    # if the issue  we are looking at has a name close to the new comic
                    # and the publishing year is the same or the next year
                    # and the issue number is the next issue
                    # then append the issue to the series
                    # if series.name_close_enough(item.title):
                    #   print(item.title + '\t'
                    #        + str((temp_Contains[index].contains[-1].pubyear - item.pubyear) in [0, 1]) + '\t'
                    #        + str((temp_Contains[index].contains[-1].issue - item.issue) == -1))

                    # if the file name is close enough, and the comic was published in the same or next year,
                    # and the issue number is within 1 or the issue number and publication year is the same and
                    # allow_duplicates is not "false"
                    if temp_Contains[index].name_close_enough(item.title) \
                            and (item.pubyear - lastissue.pubyear) in [0, 1] \
                            and ((0 < (item.issueNum - lastissue.issueNum) <= 1)
                                 or (0 == (item.issueNum - lastissue.issueNum)
                                     and (str.lower(allow_duplicates) != "false") and (
                                             item.pubyear - lastissue.pubyear == 0))):
                        # if the file is a duplicate: # Comparing issueStr instead of issueNum
                        if str.lower(allow_duplicates) == 'delete' and ((item.issueStr == lastissue.issueStr \
                                                                         and (item.pubyear - lastissue.pubyear == 0))):
                            # and the last issue is larger or the same size
                            if lastissue.size >= item.size:
                                if not test:
                                    # delete the file
                                    os.remove(item.containing_directory + "/" + item.file)
                                # And since we're not appending it to anything it will be thrown out with sortme
                            # if the lastissue was smaller:
                            else:
                                if not test:
                                    # delete the last issue
                                    # print(lastissue.containing_directory)
                                    # print(lastissue.file)
                                    os.remove(lastissue.containing_directory + "/" + lastissue.file)
                                    print("Deleted" + lastissue.title + " (" + lastissue.file + ")")
                                    # and move the file as one would normally
                                    item.move_file(temp_Contains[index].file)
                                # and append it to the collection
                                temp_Contains[index].contains.append(item)
                                print("Added " + item.title + " " + item.issueStr + " to " + temp_Contains[
                                    index].name)
                            pass
                        # if the last file was not a duplicate
                        else:
                            # Since we're checking IssueStr, 1.MU will be dropped in the same folder as issue #1
                            if not test:
                                # move the file
                                item.move_file(temp_Contains[index].file)
                            # and append it to the collection
                            temp_Contains[index].contains.append(item)
                            print("Added " + item.title + " " + item.issueStr + " to " + temp_Contains[
                                index].name)
                        # regardless of whether or not it was a duplicate
                        # setting found to true will let the next piece of code know not to create a new folder
                        found = True
                        # stop the loop
                        break
                index += 1
            if not found:
                # If there is no existing series, create a new one
                print("Created new series for " + item.title)
                if not test:
                    try:
                        createddir = "/" + item.title + " (" + str(item.pubyear) + ")" + "/"
                        item.move_file(self.location + createddir)
                        temp_Contains.append(Series(name=item.title,
                                                    location=self.location, contents=[item]))
                    except os.error:
                        print("Directory already exists: " + item.title + " (" + str(item.pubyear) + ")")
                else:
                    temp_Contains.append(Series(name=item.title, contents=[item]))

        # temp_Contains is sorted by publishing year and then reversed, such that the latest series come first.
        temp_Contains.sort(key=lambda x: x.pubyear)
        temp_Contains.reverse()

        # Sort all the special seconds
        for item in special_second:
            index = 0
            found = False
            while index < len(temp_Contains):
                series = temp_Contains[index]
                if type(series) is Series:

                    # This is different than the above because we're just finding
                    # the first series with the same name as the title that came before
                    # This code relies on temp_Contains being sorted in reverse pubYear order
                    if temp_Contains[index].name_close_enough(item.title) \
                            and ((item.pubyear >= series.pubyear)  # Check to see if this came out after the series
                                 or (0 == (item.issueNum - lastissue.issueNum)
                                     and (str.lower(allow_duplicates) != "false") and (
                                             item.pubyear - lastissue.pubyear == 0))):
                        lastissue = series.contains[-1]  # We still need to get the last issue for duplicate check
                        # this is not the issue with the largest number, but the issue which was added to the array last

                        # if the file is a duplicate: # Comparing issueStr instead of issueNum
                        if str.lower(allow_duplicates) == 'delete' and ((item.issueStr == lastissue.issueStr
                                                                         and (item.pubyear - lastissue.pubyear == 0))):
                            # and the last issue is larger or the same size
                            if lastissue.size >= item.size:
                                if not test:
                                    # delete the file
                                    os.remove(item.containing_directory + "/" + item.file)
                                # And since we're not appending it to anything it will be thrown out with sortme
                            # if the lastissue was smaller:
                            else:
                                if not test:
                                    # delete the last issue
                                    # print(lastissue.containing_directory)
                                    # print(lastissue.file)
                                    os.remove(lastissue.containing_directory + "/" + lastissue.file)
                                    print("Deleted" + lastissue.title + " (" + lastissue.file + ")")
                                    # and move the file as one would normally
                                    item.move_file(temp_Contains[index].file)
                                # and append it to the collection
                                temp_Contains[index].contains.append(item)
                                print("Added " + item.title + " " + item.issueStr + " to " + temp_Contains[
                                    index].name)
                            pass
                        # if the last file was not a duplicate
                        else:
                            if not test:
                                # move the file
                                item.move_file(temp_Contains[index].file)
                            # and append it to the collection
                            temp_Contains[index].contains.append(item)
                            print("Added " + item.title + " " + item.issueStr + " to " + temp_Contains[
                                index].name)
                        # regardless of whether or not it was a duplicate
                        # setting found to true will let the next piece of code know not to create a new folder
                        found = True
                        # stop the loop
                        break
                index += 1
            if not found:
                # If there is no existing series, create a new one
                print("Created new series for " + item.title)
                if not test:
                    try:
                        createddir = "/" + item.title + " (" + str(item.pubyear) + ")" + "/"
                        item.move_file(self.location + createddir)
                        temp_Contains.append(Series(name=item.title,
                                                    location=self.location, contents=[item]))
                    except os.error:
                        print("Directory already exists: " + item.title + " (" + str(item.pubyear) + ")")
                else:
                    # ToDo: Add in the ability to update to existing series under certain circumstances
                    temp_Contains.append(Series(name=item.title, contents=[item]))

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
