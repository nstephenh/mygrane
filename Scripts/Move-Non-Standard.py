import os
import re

walk = os.walk(".")
for directory in walk:
    for filename in directory[2]:
        error = False
        yearregex = re.compile("[1-2][90]\d\d")
        try:
            pubyear = int(yearregex.findall(filename)[-1])
            try:
                frontpart =filename.split('(')[0]
            except Exception as e:
                print("File does not have a parentheisis")
                print(e)
                error = True
        except Exception:
            print("Unable to find year of publication")
            error = True
        if error:
            print(filename)
            os.system("mv '" + filename + "' 00Sort/")
