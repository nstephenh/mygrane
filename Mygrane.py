# Main controller for a mygrane instance
import argparse
import mygrane
import mygrane.collection

Library = None


def main():
        print("Starting instance of Mygrane")
        parser = argparse.ArgumentParser(description='Comic Library Manager')
        parser.add_argument("-l", help="Directory where comics are stored")
        parser.add_argument("--config", help="directory for config files")

        # Load information from config file if not specified as arguments
        args = parser.parse_args()
        #libLoc = args[0]
        libLoc = "/home/nsh/Documents/Comics To Read/All of Marvel"

        # Run a loop of asking for commands and running them.
        end = False
        while (not end):
            try:
                userinput = input("> ")
                cmd = userinput.lower().split(" ")[0]
                if cmd == "help":
                    print("""Available commands:
                          quit         -- Quits Mygrane
                          init <loc>        -- Initializes Library
                          sort         -- Sorts library
                          print        -- Prints library contents
                            """)
                elif cmd == "init":
                    try:
                        path = " ".join(userinput.split(" ")[1:])
                        if not path is "":
                            libLoc = path
                    except Exception:
                        # Path not provided, assume one is already provided
                        pass
                    if libLoc is None:
                        raise Exception("No Library provided")
                    print("Opening library at location: " + libLoc)
                    Library = mygrane.collection.Collection(libLoc)
                elif cmd in ["print", "ls"]:
                    if Library is None:
                        raise Exception("No Library provided")
                    print(Library)
            except Exception:
                print(type(Exception))
                print(Exception)



if __name__ == "__main__":
    main()