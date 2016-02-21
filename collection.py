import os
import zipfile



class Series:
    def __init__(self, containing_directory):
        for file in os.listdir(containing_directory):
            extension = (file.split(".")[-1])
            if extension in ["cbr", "cbz"]:
                print(file)
                if extension == "cbz":
                    zf = zipfile.ZipFile(file)
                    zf.extractall("./tmp")
                os.remove("./tmp/*")




