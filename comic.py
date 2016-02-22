import os
import zipfile
from unrar import rarfile
import gi
gi.require_version('Gtk', '3.0')
from gi.repository.GdkPixbuf import Pixbuf, PixbufLoader

from preferences import *


class Comic:

    def __init__(self, containing_directory, file):
        self.thumbnail = None
        self.containing_directory = containing_directory
        self.file = file
        extension = (file.split(".")[-1])
        if extension in ["cbr", "cbz", "rar", "zip"]:
            print(file)
            if extension in ("cbz", "zip"):
                self.set_thumbnail_from_zip()
            if extension in ("cbr", "zip"):
                self.set_thumbnail_from_rar()

    def set_thumbnail_from_zip(self):
        zf = zipfile.ZipFile(self.containing_directory + "/" + self.file)
        for file_in_zip in zf.namelist()[:2]:
            if ".jpg" in file_in_zip.lower() or ".png" in file_in_zip.lower():
                #print("Found image: ", file_in_zip, " -- ")
                cover = zf.read(file_in_zip)
                zf.close()
                return self.set_thumbnail(cover)
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
                return self.set_thumbnail(cover)
            else:
                pass
                #print("First image not an image: " + file_in_rar)
        return False

    def set_thumbnail(self, image_to_use):
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
