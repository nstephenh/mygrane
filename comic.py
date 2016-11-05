import os
import zipfile
from unrar import rarfile
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository.GdkPixbuf import Pixbuf, PixbufLoader

from preferences import *

import re
import hashlib
import shutil

class Comic:
    """
    Object that represents a comic. Contains the following information
    containing_directory - The location of the comic
    file - the filename of the comic in containing_directory
    extension - the extension of the comic
    thumbnail - a pixbuf of the first page of the comic

    pubyear - The year of publication of the comic, automatically determined by the last string in the filename matching
        the regex "[1-2][90]\d\d"
    issue - Issue number
    title - The title of the comic
    """

    def __init__(self, containing_directory, file):
        self.thumbnail = None
        self.containing_directory = containing_directory
        self.file = file
        self.extension = (file.split(".")[-1].lower)
        self.pubyear = 0
        self.title = ""
        self.issue = None
        self.isTPB = False
        self.tags = []
        self.set_info_from_name()
        junk = self.title + str(self.issue) + str(self.pubyear) + self.containing_directory.split('/')[-1]
        self.ident = hashlib.md5(junk.encode()).hexdigest()

    def __str__(self):
        return self.title + " " + str(self.issue) + " (" + str(self.pubyear) + ")"

    def move_file(self, dir_name=None, series=None):
        """

        :param dir_name: moves the file to this directory (asbsolute path)
        :param series: move the file to within this series
        :return: True if no errors thrown
        """
        olditemdir = self.containing_directory + "/"
        if series:
            self.title = series.name
            self.containing_directory = series.file + "/"
        if dir_name:
            self.containing_directory = dir_name
        try:
            shutil.move(olditemdir + self.file, self.containing_directory + self.file)
            try:
                os.rmdir(olditemdir)  # This is to remove empty directories
                print("Removed empty directory for " + self.file)
            except os.error as g:
                pass
            return True
        except OSError as e:
            try:
                os.mkdir(self.containing_directory)
                shutil.move(olditemdir + self.file, self.containing_directory + self.file)
                return True
            except OSError as f:
                print("Error, comic already exists in directory or")
                print(e)
                return False

    def set_info_from_name(self):
        self.tags = re.findall("\((.^)\)", self.file)
        yearregex = re.compile("\(([1-2][90]\d\d)\)")
        try:
            self.pubyear = int(yearregex.findall(self.file)[-1])
            try:
                frontpart = self.file.split('(')[0]
                try:
                    # This is a depreciated format, scanners should use "(2 covers)" instead of "02 of 04 covers"
                    coversplit = re.split('\d{1,2} of \d{1,2} covers', frontpart, flags=re.IGNORECASE)[0].strip()
                except Exception:
                    print("Not using alt covers")

                issuestring = coversplit.split()[-1]
                try:
                    self.issue = float(issuestring)  # Using floats adds supports for .1 issues, etc
                except Exception:
                    # In case the issue number is something like 15AU, try stripping out not numeric characters
                    try:
                        issuestring = re.sub("[^0-9]", "", issuestring)
                        self.issue = float(issuestring)
                    except Exception:
                        # Comic has no issuenumber
                        self.title = coversplit
                        return
                frontpart = coversplit

                #throw out volume numbers
                try:
                    frontpart = re.sub(" v\d{1,2} ", " ", frontpart)
                except Exception:
                    pass

                try:
                    longname = " ".join(frontpart.split()[:-1])
                    #left this in in case its important
                    if re.match("v\d{1,2}", longname.split()[-1]):
                        self.title = " ".join(longname.split()[:-1])
                        print("its got a volume number")
                    else:
                        self.title = longname
                except Exception:
                    print("File does not do something")
            except Exception as e:
                print("File does not have a parentheisis")
                print(e)
        except Exception:
            print("Unable to find year of publication")

    def set_thumbnail(self):
        coverimageloc = datadir + "/" + str(self.ident) + ".cover"
        if os.path.isfile(coverimageloc):
            try:
                self.thumbnail = Pixbuf.new_from_file(coverimageloc)
            except Exception:
                pass
            # Look for a thumbnail file already made
        else:
            try:
                switch = self.extension
                if switch in ("cbz", "zip"):
                    self.set_thumbnail_from_zip()
                elif switch in ("cbr", "zip"):
                    self.set_thumbnail_from_rar()
                    self.thumbnail.savev(coverimageloc, 'png', [None], [None])
            except AttributeError:
                print("That ain't a comic!")


    def set_thumbnail_from_zip(self):
        zf = zipfile.ZipFile(self.containing_directory + "/" + self.file)
        for file_in_zip in zf.namelist()[:2]:
            if ".jpg" in file_in_zip.lower() or ".png" in file_in_zip.lower():
                #print("Found image: ", file_in_zip, " -- ")
                cover = zf.read(file_in_zip)
                zf.close()
                return self.set_thumbnail_to_image(cover)
            else:
                pass
                #print("First image not an image: " + file_in_zip)
        return False

    def set_thumbnail_from_rar(self):
        rf = rarfile.RarFile(self.containing_directory + "/" + self.file)
        for file_in_rar in sorted(rf.namelist())[:2]:
            if ".jpg" in file_in_rar.lower() or ".png" in file_in_rar.lower():
                #print("Found image: ", file_in_rar, " -- ")
                cover = rf.read(file_in_rar)
                return self.set_thumbnail_to_image(cover)
            else:
                pass
                #print("First image not an image: " + file_in_rar)
        return False

    def set_thumbnail_to_image(self, image_to_use):
        try:
            loader = PixbufLoader()
            loader.write(image_to_use)
            loader.close()
            thumbnail = loader.get_pixbuf()
            h = thumbnail.get_height()
            w = thumbnail.get_width()
            r = h/w  # Preserve Aspect Ratio
            pixbuf = Pixbuf.scale_simple(thumbnail, cover_width, cover_width*r, True)
            self.thumbnail = pixbuf
            return True
        except Exception:
            print(Exception)
            return False
