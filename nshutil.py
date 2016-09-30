import os
def move(src,dest):
    try:
        os.rename(src, dest)
    except (OSError, IOError) as E:
        if E.errno == 2:
            raise OSError
        os.system("mv '''" + src + "''' '''" + dest + "'''")
