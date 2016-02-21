import os
import zipfile
import io
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository.GdkPixbuf import Pixbuf, PixbufLoader
from gi.repository import Gio



class Series:

    contains = []
    def __init__(self, containing_directory):
        for file in os.listdir(containing_directory):
            extension = (file.split(".")[-1])
            if extension in ["cbr", "cbz"]:
                print(file)
                if extension == "cbz":
                    zf = zipfile.ZipFile(containing_directory + "/" + file)
                    file_in_zip = zf.namelist()[0]
                    if (".jpg" in file_in_zip or ".png" in file_in_zip):
                        print("Found image: ", file_in_zip, " -- ")
                        loader = PixbufLoader()
                        loader.write(zf.read(file_in_zip))
                        loader.close()
                        img = loader.get_pixbuf()
                        self.contains.append([img])
                    else:
                        print("First image not an image")
                #os.remove("./tmp/*")




