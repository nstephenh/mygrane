from mygrane import preferences


def log(log_string):
    if preferences.verbose:
        print(log_string)
