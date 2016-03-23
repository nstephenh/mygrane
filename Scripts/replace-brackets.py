import os
import re

walk = os.walk(".")
for directory in walk:
    for filename in directory[2]:
        newname = filename
        newname = re.sub("\[", '(', newname)
        newname = re.sub("\]", ')', newname)
        if newname != filename:
            print('mv \"' + filename + "\" \"" + newname + "\"")
            os.system('mv \"' + filename + "\" \"" + newname + "\"")
