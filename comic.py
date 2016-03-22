import os
import zipfile
from unrar import rarfile
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('GdkPixbuf', '2.0')
from gi.repository.GdkPixbuf import Pixbuf, PixbufLoader

from preferences import *

import re

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
        self.extension = (file.split(".")[-1])
        self.pubyear = 0
        self.title = ""
        self.issue = 0
        self.set_info_from_name()

    def __str__(self):
        return self.title + " " + str(self.issue) + " (" + str(self.pubyear) + ")"

    def set_info_from_name(self):
        yearregex = re.compile("[1-2][90]\d\d")
        try:
            self.pubyear = int(yearregex.findall(self.file)[-1])
            try:
                frontpart = self.file.split('(')[0]
                try:
                    # This is a depreciated format, scanners should use "(2 covers)" instead of "02 of 04 covers"
                    coversplit = re.split('\d{1,2} of \d{1,2} covers', frontpart, flags=re.IGNORECASE)[0].strip()
                    self.issue = int(coversplit.split()[-1])
                    frontpart = coversplit
                except Exception:
                    print("Not using alt covers")
                self.issue = int(frontpart.split()[-1])
                try:
                    longname = " ".join(frontpart.split()[:-1])
                    if re.match("v\d", longname.split()[-1]):
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
        switch  = self.extension;
        if switch in ("cbz", "zip"):
            self.set_thumbnail_from_zip()
        elif switch in ("cbr", "zip"):
            self.set_thumbnail_from_rar()
        else:
            pass

    def set_thumbnail_from_zip(self):
        zf = zipfile.ZipFile(self.containing_directory + "/" + self.file)
        for file_in_zip in zf.namelist()[:2]:
            if ".jpg" in file_in_zip.lower() or ".png" in file_in_zip.lower():
                #print("Found image: ", file_in_zip, " -- ")
                cover = zf.read(file_in_zip)
                zf.close()
                return self.set_thumbnail_to_file(cover)
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
                return self.set_thumbnail_to_file(cover)
            else:
                pass
                #print("First image not an image: " + file_in_rar)
        return False

    def set_thumbnail_to_file(self, image_to_use):
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
