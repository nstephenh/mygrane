class nshutil:
    def move(src,dest):
        try:
            os.rename(src, dest)
        except OSError:
            os.system("mv '''" + src + "''' '''" + dest + "'''")
