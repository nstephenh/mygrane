import os

input_directory = os.getenv("INPUT_DIRECTORY")
library_directory = os.getenv("LIBRARY_DIRECTORY")

use_links = True
hardlink = True  # Use Hardlinks by default, switch to symlinks if false

verbose = False

single_issues_get_series = True
