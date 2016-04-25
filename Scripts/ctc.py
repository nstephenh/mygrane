import os
import re
walk = os.listdir(".")

ctcstring = """\(\((ctc)\)\)"""
for filename in walk:
    extension = filename.split(".")[-1]
    if extension == "cbz" or extension == "cbr":
        try:
            pos = filename.find(ctcstring)
            print(ctcstring)
            print(filename)
            if ctcstring in filename:
                 newname = filename[:pos] + filename[pos+len(ctcstring)+1:]
            else:
                 newname = filename
        except Exception as e:
            newname = filename
            print(e)
        try:
            pgcount = re.search("\( \d{1,3}p", newname).group(0)
            #newname = re.sub(pgcount, "(" + pgcount[2:] + ")", newname)
        except Exception as e:
            #print(e)
            pass

        if not newname == filename:
            print("Renaming " +  filename + " to " + newname)
            print()
            os.rename(filename, newname)
