#!/usr/bin/python3

# Main controller for a mygrane instance
import argparse

import mygrane
import mygrane.collection


def main():
    print("Starting instance of Mygrane")
    parser = argparse.ArgumentParser(description='Comic Library Manager')
    parser.add_argument("-l", help="Directory where comics are stored")
    parser.add_argument("--config", help="directory for config files")

    # Load information from config file if not specified as arguments
    lib_loc = None
    library = None

    # Run a loop of asking for commands and running them.
    end = False
    while (not end):
        try:
            userinput = input("> ")
            cmd = userinput.lower().split(" ")[0]
            if cmd == "help":
                print("""
Available commands:
    quit            Quits Mygrane
    init <loc>      Initializes Library
    test            Runs a sort in "Test mode" where it does not move any files
    sort            Sorts library, not allowing duplicates
    sortdupes       Sorts library, allowing duplicates
    sortdelete      Sorts library, deleting duplicates
    print           Prints library contents
""")
            elif cmd == "init":
                try:
                    path = " ".join(userinput.split(" ")[1:])
                    if path != "":
                        lib_loc = path
                except Exception:
                    # Path not provided, assume one is already provided
                    pass
                if lib_loc is None:
                    raise Exception("No Library provided")
                print("Opening library at location: " + lib_loc)
                library = mygrane.collection.Collection(lib_loc)
            elif cmd in ["print", "ls"]:
                if library is None:
                    raise Exception("No Library provided")
                print(library)
            elif cmd in ["sort"]:
                if library is None:
                    raise Exception("No Library provided")
                try:
                    library.sort(test=False, allow_duplicates="False")
                except Exception as detail:
                    print(detail)
            elif cmd in ["test"]:
                if library is None:
                    raise Exception("No Library provided")
                try:
                    library.sort(test=True, allow_duplicates="False")
                except Exception as detail:
                    print(detail)
            elif cmd in ["sortdupes"]:
                if library is None:
                    raise Exception("No Library provided")
                try:
                    library.sort(test=False, allow_duplicates="True")
                except Exception as detail:
                    print(detail)
            elif cmd in ["sortdelete"]:
                if library is None:
                    raise Exception("No Library provided")
                try:
                    library.sort(test=False, allow_duplicates="Delete")
                except Exception as detail:
                    print(detail)
        except Exception as detail:
            print(detail)


if __name__ == "__main__":
    main()
