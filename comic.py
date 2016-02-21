import os
import zipfile
from unrar import rarfile
import gi
gi.require_version('Gtk', '3.0')
from gi.repository.GdkPixbuf import Pixbuf, PixbufLoader





class Comic:

    thumbnail = None
    name = ""
    containing_directory = ""
    file = ""

    def __init__(self, containing_directory, file):
        self.containing_directory = containing_directory
        self.file = file

    def set_thumbnail_from_zip(self):
        zf = zipfile.ZipFile(self.containing_directory + "/" + self.file)
        for file_in_zip in zf.namelist()[:2]:
            if ".jpg" in file_in_zip.lower() or ".png" in file_in_zip.lower():
                print("Found image: ", file_in_zip, " -- ")
                return self.set_thumbnail(zf.read(file_in_zip))
            else:
                print("First image not an image: " + file_in_zip)
        return False

    def set_thumbnail_from_rar(self):
        rf = rarfile.RarFile(self.containing_directory + "/" + self.file)
        for file_in_rar in sorted(rf.namelist())[:2]:
            if ".jpg" in file_in_rar.lower() or ".png" in file_in_rar.lower():
                print("Found image: ", file_in_rar, " -- ")
                return self.set_thumbnail(rf.read(file_in_rar))
            else:
                print("First image not an image: " + file_in_rar)
        return False



    def set_thumbnail(self, image_to_use):
        try:
            loader = PixbufLoader()
            loader.write(image_to_use)
            loader.close()
            self.thumbnail = loader.get_pixbuf()
            return True
        except Exception:
            print(Exception)
            return False
