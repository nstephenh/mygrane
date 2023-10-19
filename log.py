from mygrane import preferences

logfile = open("log.txt", "w")


def log(log_string):
    logfile.write(log_string + "\n")
    if preferences.verbose:
        print(log_string)
