import os

def bring_out(path):
    for thing in sorted(os.listdir(path)):
            absPath = path + "/" + thing
            if os.path.isdir(absPath):
                bring_out(absPath)
                print(thing)
                os.rename(absPath, thing)


for item in sorted(os.listdir(".")):
    if os.path.isdir(item):
        print(item)
        bring_out(item)
