from mygrane import preferences
from mygrane.collection import Collection

if preferences.input_directory is None:
    print("Please specify an input directory")
    exit()

stuff = Collection()
stuff.sort(test=False, allow_duplicates="True")
stuff.write_info_file()
