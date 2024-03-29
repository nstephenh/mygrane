"""
This file was created because I accidentally removed a parameter from the series constructor,
which set the location of each series to be the file location.
This was a bad idea, and it made a ton of unnecessary hardlinks in the "0-days" directory.
It can be used in general to delete all the links made by mygrane, using the links index.
"""
import json
import os

if __name__ == "__main__":

    with open("../index_links.json", "r") as fp:
        index_links = json.load(fp)

        for link_path in index_links.keys():
            if link_path is None or link_path == "null":
                continue  # skip null case
            print(f"Removing {link_path}")
            try:
                os.unlink(link_path)
            except Exception as e:
                print("\tFile was not there!")
    os.remove("../index_links.json")
