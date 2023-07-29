import os
import re

import tqdm

from log import log
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
        self.location = location
        # log(contents) # debug line
        if contents != []:
            self.contains = contents
            self.location = self.contains[0].containing_directory  # Should be absolute...
        elif self.location != "":
            self.contains = []
            log("Initializing " + location)
            for file in sorted(os.listdir(location)):
                log(file)
                extension = (file.split(".")[-1])
                if extension.lower() in ["cbr", "cbz", "rar", "zip", "pdf"]:
                    issue = Comic(location, file)
                    self.contains.append(issue)
        elif self.name != "":
            self.location = os.path.join(preferences.library_directory, name)
        # log(self.filename) #Debug line
        if name == "":
            # log(self.filename)
            log(self.contains)
            self.name = self.contains[0].title
        self.pubyear = self.contains[0].pubyear

    def __str__(self):
        return "{} ({})".format(self.title, self.pubyear)

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
            log("Creating new collection")
            for item in sorted(os.listdir(location)):
                sublocation = location + "/" + item
                if os.path.isdir(sublocation):
                    # log(item)
                    if flatten == False:
                        self.contains.append(Series(sublocation))
                    else:
                        # If flatten is true then we want to cycle through each item
                        for subitem in sorted(os.listdir(sublocation + "/")):
                            self.contains.append(Comic(sublocation + "/", subitem))
                else:
                    try:
                        item.encode("UTF-8")
                        log("Adding " + item + " To collection")
                        newcomic = Comic(location, item)
                        self.contains.append(newcomic)
                    except UnicodeEncodeError as ude:
                        log("Error adding item: " + sublocation.encode('utf-8', 'ignore').decode('utf-8'))
        elif len(contains) != 0:
            for item in contains:
                self.contains.append(item)
                if self.location == "" and type(item) is Series:
                    self.location = self.contains[0].filename
        else:
            self.location = preferences.library_directory
            total = 0
            progress_bar = tqdm.tqdm(desc="Files scanned", total=100, unit="Files")
            for root, _, filenames in os.walk(preferences.input_directory):
                total += len(filenames)
                progress_bar.total = total
                progress_bar.refresh()
                for filename in sorted(filenames):
                    progress_bar.update(1)
                    log(root + "/" + filename)
                    self.contains.append(Comic(root, filename))
            progress_bar.close()
            if preferences.use_links:
                # Find existing links to files in the library
                progress_bar = tqdm.tqdm(desc="Checking existing library", total=total, unit="Files")
                for root, _, filenames in os.walk(preferences.library_directory):
                    for filename in sorted(filenames):
                        progress_bar.update(1)
                        path = root + "/" + filename
                        log(path)
                        comic = next((comic for comic in self.contains if comic.filename == filename), None)
                        if comic is not None:
                            comic.link_path = path
                progress_bar.close()

                # Test that these symlinks were found and saved on the objects properly:
                total_links = 0
                progress_bar = tqdm.tqdm(desc="Counting Links", total=total, unit="Files")
                for comic in self.contains:
                    if comic.link_path is not None:
                        total_links += 1
                        progress_bar.update(1)
                progress_bar.close()
                print("Total links {} of {}".format(total_links, total))

    def sort(self, test=True, allow_duplicates="False"):
        """

        :param test:
        :param allow_duplicates: "true" "false" or "delete". Delete will keep the copy with the highest filesize
        :return:
        """
        contains = []  # New contents
        sortme = []  # This is what we use as a temporary container.
        special_second = []  # Issues with strange numbers like #0 or 0.MU, that may have come out after issue 1.

        # The following handles comics with no issue number by skipping them for the sort
        for item in self.contains:
            if type(item) is Comic:
                if item.issueNum is None:
                    # Trade Paperback or other item, has no issue number
                    contains.append(item)
                elif item.issueNum < 1:
                    # 0 issue or 0.1 issue, will go through on secondary pass
                    special_second.append(item)
                else:
                    # regular issues
                    sortme.append(item)
            else:
                # Series Objects
                contains.append(item)

        # TODO: Make issue 1 come before issue 1.MU, etc....

        sortme.sort(key=lambda x: x.title)  # sort by title for an order

        # presort sort to go by issue number
        sortme.sort(key=lambda x: x.issueStr)  # hopefully fixes above todo^
        sortme.sort(key=lambda x: x.issueNum)
        special_second.sort(key=lambda x: x.issueNum)

        total = len(sortme)
        bar = tqdm.tqdm(total=total, desc='Sorting', position=0, unit="Comics")

        # sort each comic into its own series
        for item in sortme:
            # reset candidate index
            candidate_index = 0
            found = False
            # iterate over each existing issue and see if it is the same series
            while candidate_index < len(contains):
                candidate = contains[candidate_index]
                if type(candidate) is Series:
                    series = candidate
                    last_issue = series.contains[-1]
                    # if the issue  we are looking at has a name close to the new comic
                    # and the publishing year is the same or the next year
                    # and the issue number is the next issue
                    # then append the issue to the series
                    # if series.name_close_enough(item.title):
                    #   log(item.title + '\t'
                    #        + str((series.contains[-1].pubyear - item.pubyear) in [0, 1]) + '\t'
                    #        + str((series.contains[-1].issue - item.issue) == -1))

                    # if the filename name is close enough, and the comic was published in the same or next year,
                    # and the issue number is within 1 or the issue number and publication year is the same and
                    # allow_duplicates is not "false"
                    if series.name_close_enough(item.title) \
                            and (item.pubyear - last_issue.pubyear) in [0, 1] \
                            and ((0 < (item.issueNum - last_issue.issueNum) <= 1)
                                 or (0 == (item.issueNum - last_issue.issueNum)
                                     and (str.lower(allow_duplicates) != "false") and (
                                             item.pubyear - last_issue.pubyear == 0))):
                        log("Match found")
                        # if we are deleting or using links, and issue is the same, this is a duplicate to skip:
                        if (str.lower(allow_duplicates) == 'delete' or preferences.use_links) and (
                                item.issueStr == last_issue.issueStr and (item.pubyear - last_issue.pubyear == 0)):
                            log("Not transferring duplicate")

                            # and the last issue is larger or the same size
                            if last_issue.size >= item.size:
                                if not test and str.lower(allow_duplicates) == 'delete':
                                    # delete the filename
                                    os.remove(item.containing_directory + "/" + item.filename)
                                    bar.write("Deleted" + item.title + " (" + item.filename + ")")

                                # Not adding it to the new collection stops us from tracking it.
                            # if the last_issue was smaller we will remove it and make a new issue
                            else:
                                log("Removing old issue")
                                if not test and str.lower(allow_duplicates) == 'delete':
                                    # delete the last issue
                                    os.remove(last_issue.containing_directory + "/" + last_issue.filename)
                                    bar.write("Deleted" + last_issue.title + " (" + last_issue.filename + ")")
                                # move the new file as one would normally
                                item.move_file(series.location)
                                # and append it to the collection
                                series.contains.append(item)
                                bar.write("Added {} to {}".format(item, series))
                        # otherwise, it's the next issue
                        else:
                            # Since we're checking IssueStr, 1.MU will be dropped in the same folder as issue #1
                            if not test:
                                # move the file
                                item.move_file(series.location)
                            # and append it to the collection
                            series.contains.append(item)
                            bar.write("Added {} to {}".format(item, series))
                        # regardless of whether it was a duplicate
                        # setting found to true will let the next piece of code know not to create a new folder
                        found = True
                        # stop the loop
                        break
                candidate_index += 1
            if not found:
                # If there is no existing series, create a new one
                bar.write("Created new series for {} ({})".format(item.title, item.filename))
                if not test:
                    new_series_dir = "/" + item.title + " (" + str(item.pubyear) + ")" + "/"
                    item.move_file(self.location + new_series_dir)
                    contains.append(Series(name=item.title,
                                           location=self.location, contents=[item]))
                else:
                    contains.append(Series(name=item.title, contents=[item]))
            bar.update(1)
        bar.close()

        # contains is sorted by publishing year and then reversed, such that the latest series come first.
        contains.sort(key=lambda x: x.pubyear)
        contains.reverse()

        # Sort all the special seconds
        for item in special_second:
            candidate_index = 0
            found = False
            while candidate_index < len(contains):
                series = series
                if type(series) is Series:

                    # This is different from the above because we're just finding
                    # the first series with the same name as the title that came before
                    # This code relies on contains being sorted in reverse pubYear order
                    if series.name_close_enough(item.title) \
                            and ((item.pubyear >= series.pubyear)  # Check to see if this came out after the series
                                 or (0 == (item.issueNum - last_issue.issueNum)
                                     and (str.lower(allow_duplicates) != "false") and (
                                             item.pubyear - last_issue.pubyear == 0))):
                        last_issue = series.contains[-1]  # We still need to get the last issue for duplicate check
                        # this is not the issue with the largest number, but the issue which was added to the array last

                        # if the filename is a duplicate: # Comparing issueStr instead of issueNum
                        if str.lower(allow_duplicates) == 'delete' and ((item.issueStr == last_issue.issueStr
                                                                         and (item.pubyear - last_issue.pubyear == 0))):
                            # and the last issue is larger or the same size
                            if last_issue.size >= item.size:
                                if not test:
                                    # delete the filename
                                    os.remove(item.containing_directory + "/" + item.filename)
                                # And since we're not appending it to anything it will be thrown out with sortme
                            # if the last_issue was smaller:
                            else:
                                if not test:
                                    # delete the last issue
                                    # log(last_issue.containing_directory)
                                    # log(last_issue.filename)
                                    os.remove(last_issue.containing_directory + "/" + last_issue.filename)
                                    log("Deleted" + last_issue.title + " (" + last_issue.filename + ")")
                                    # and move the filename as one would normally
                                    item.move_file(series.location)
                                # and append it to the collection
                                series.contains.append(item)
                                log("Added " + item.title + " " + item.issueStr + " to " + contains[
                                    candidate_index].name)
                            pass
                        # if the last filename was not a duplicate
                        else:
                            if not test:
                                # move the filename
                                item.move_file(series.location)
                            # and append it to the collection
                            series.contains.append(item)
                            log("Added " + item.title + " " + item.issueStr + " to " + contains[
                                candidate_index].name)
                        # regardless of whether it was a duplicate
                        # setting found to true will let the next piece of code know not to create a new folder
                        found = True
                        # stop the loop
                        break
                candidate_index += 1
            if not found:
                # If there is no existing series, create a new one
                log("Created new series for " + item.title)
                if not test:
                    try:
                        new_series_dir = "/" + item.title + " (" + str(item.pubyear) + ")" + "/"
                        item.move_file(self.location + new_series_dir)
                        contains.append(Series(name=item.title,
                                               location=self.location, contents=[item]))
                    except os.error:
                        log("Directory already exists: " + item.title + " (" + str(item.pubyear) + ")")
                else:
                    # ToDo: Add in the ability to update to existing series under certain circumstances
                    contains.append(Series(name=item.title, contents=[item]))

        # Skip this if we are using symlinks since the symlink move code can't remove the existing symlink
        if not preferences.single_issues_get_series or preferences.use_links:
            # If series only contains one item, make it a comic object

            candidate_index = 0
            for item in contains:
                if type(item) is Series and len(item.contains) == 1:
                    if not test:
                        # Move the filename out of empty the collection
                        single = item.contains[0]
                        single.move_file(self.location)
                candidate_index += 1

        self.contains = contains
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
