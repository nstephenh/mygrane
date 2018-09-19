#!/usr/bin/python3
# Main controller for a mygrane instance
import argparse
import configparser
import mygrane
import mygrane.collection
#import mygrane.webserve

import _thread
#import tornado

Library = None


def main():
    parser = argparse.ArgumentParser(description='Comic Library Manager')
    parser.add_argument("--initdb", help="Initialize a database in the default directory")
    parser.add_argument("--db", help="Alternate database location", type=str)


    parser.add_argument("--importdir", help="Import all comics in a specified import directory (recursive)")
    parser.add_argument("--mv", help="flag move all comics to specified directory", type=str)
    parser.add_argument("--format", help="Specify format for names")


    args = parser.parse_args()

    #Init variables like db location
    db = "./database.sqlite"
    if args.db:
        db = args.db

    #Run selected command
    if args.initdb:
        pass
    elif args.importdir:
        pass
    elif args.list:
        pass



if __name__ == "__main__":
    main()