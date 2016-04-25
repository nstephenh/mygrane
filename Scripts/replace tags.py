import os
import re
walk = os.listdir(".")
for filename in walk:
    extension = filename.split(".")[-1]
    if extension == "cbz" or extension == "cbr":
        try:
            newname = re.sub(" ctc", "(ctc)", filename)
        except Exception:
            newname = filename
        try:
            pgcount = re.match(" \d{1,3}p", newname).group(1)
            newname = re.sub(pgcount, "(" + pgcount + ")", newname)
            print(Exception)
        except Exception:
            pass

        if not newname == filename:
            print("Renaming %s to %s", filename, newname)
            os.rename(filename, newname)
