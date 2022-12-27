import os
import re
import shutil
import zipfile

import mygrane.preferences as settings
from log import log


class Comic:
    """
    Object that represents a comic. Contains the following information
    containing_directory - The location of the comic
    filename - the filename of the comic in containing_directory
    extension - the extension of the comic
    thumbnail - a pixbuf of the first page of the comic

    pubyear - The year of publication of the comic, automatically determined by the last string in the filename matching
        the regex "[1-2][90]\d\d"
    issue - Issue number
    title - The title of the comic
    """

    def __init__(self, containing_directory, filename):
        self.thumbnail = None
        self.containing_directory = containing_directory
        self.symlink_location = None
        self.filename = filename
        self.extension = filename.split(".")[-1].lower()
        self.size = os.path.getsize(containing_directory + "/" + filename)
        self.pubyear = 0
        self.title = ""
        self.issueStr = None  # string
        self.issueNum = None  # float
        self.isTPB = False
        self.tags = []
        self.set_info_from_name()

    def __str__(self):
        return self.title + " " + str(self.issueStr) + " (" + str(self.pubyear) + ")"

    @property
    def source_path(self):
        return self.containing_directory + "/" + self.filename

    def move_file(self, dir_name=None):

        old_dir = self.containing_directory + "/"
        old_path = self.source_path

        if dir_name:
            self.containing_directory = dir_name
        if old_dir == self.containing_directory:
            return True

        new_path = dir_name + self.filename

        if not os.path.isdir(dir_name):
            try:
                os.mkdir(self.containing_directory)
            except OSError as h:
                log("Error creating directory")
                log(h)

        if settings.use_symlinks:
            log("Creating a symlink for {} from {} to {}".format(self.filename, old_dir, dir_name))
            if os.path.exists(new_path):
                os.unlink(new_path)
                log("Cleared old symlink")

            try:
                os.symlink(old_path, new_path)
                return True
            except Exception as e:
                log(e)
                exit()
            return False

        log("Moving {} from {} to {}".format(self.filename, old_dir, dir_name))

        try:
            shutil.move(old_path, new_path)
            try:
                os.rmdir(old_dir)  # This is to remove empty directories
                log("Removed empty directory for " + self.filename)
            except os.error as g:
                pass
            return True
        except OSError as e:
            try:
                shutil.move(old_path, new_path)
                return True
            except OSError as f:
                log("Error, comic already exists in directory or")
                log(e)
                return False

    def set_info_from_name(self):
        self.tags = re.findall("\((.^)\)", self.filename)
        year_regex = re.compile("\(([1-2][90]\d\d)\)")
        try:
            self.pubyear = int(year_regex.findall(self.filename)[-1])
            try:
                frontpart = self.filename.split('(')[0]
                try:
                    # This is a depreciated format, scanners should use "(2 covers)" instead of "02 of 04 covers"
                    coversplit = re.split('\d{1,2} of \d{1,2} covers', frontpart, flags=re.IGNORECASE)[0].strip()
                except Exception:
                    log("Not using alt covers")
                    coversplit = frontpart

                self.issueStr = re.sub("#", "", coversplit.split()[-1])  # Grab last substring before issue name
                # and remove "#"

                try:
                    self.issueNum = float(self.issueStr)  # Using floats adds supports for .1 issues, etc
                except Exception:
                    # In case the issue number is something like 15AU, try stripping out not numeric characters
                    try:
                        issuestring = re.sub("[^.0-9]", "", self.issueStr)
                        self.issueNum = float(self.issueStr)
                    except Exception:
                        # Comic has no issuenumber
                        # And is therefore probably a Trade Paperback
                        self.title = coversplit
                        return
                frontpart = coversplit

                # throw out volume numbers
                try:
                    frontpart = re.sub(" v\d{1,2} ", " ", frontpart)
                    frontpart = re.sub(" Vol\d{1,2} ", " ", frontpart)
                except Exception:
                    pass

                try:
                    longname = " ".join(frontpart.split()[:-1])
                    self.title = longname

                except Exception:
                    log("File does not do something")
            except Exception as e:
                log("File does not have a parentheisis")
                log(e)
        except Exception:
            log("Unable to find year of publication")

    def add_to_db(self, dbcursor):
        dbcursor.execute('ADD ')
