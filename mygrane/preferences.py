import os

from dotenv import load_dotenv

load_dotenv()

input_directory = os.getenv("INPUT_DIRECTORY")
library_directory = os.getenv("LIBRARY_DIRECTORY")
incoming_directory = os.getenv("INCOMING_DIRECTORY")

air_host = os.getenv("AIR_HOST")
air_user = os.getenv("AIR_USER")
air_pass = os.getenv("AIR_PASS")
air_target_folder = os.getenv("AIR_TARGET_FOLDER") or os.getenv("AIR_SHARE_PATH") or "NewScans"
air_share_path = air_target_folder
air_hub = os.getenv("AIR_HUB")
air_target_user = os.getenv("AIR_TARGET_USER") or os.getenv("AIR_USER_NICK")
air_user_nick = air_target_user
air_share_profile = os.getenv("AIR_SHARE_PROFILE")


use_links = True
hardlink = True  # Use Hardlinks by default, switch to symlinks if false

verbose = os.getenv("VERBOSE", "").lower() in ("true", "1", "yes")

single_issues_get_series = True
