#!/usr/bin/env python3

import os
import sys
import re
from datetime import date
import sqlite3

allowed_extensions = ['cbz', 'cbr', 'pdf']
database_dir = "../comics"

import comic

import commander
interfacemode = sys.argv[1].lower()
print ("starting in mode: "+ interfacemode)
if interfacemode == 'cli':
	commander.cli.start_cli()
elif interfacemode == 'test':
	pass
