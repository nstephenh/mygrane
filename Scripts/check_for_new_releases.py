import argparse
from datetime import date
from pathlib import Path
import re
import sys
from typing import Any, Dict, List, Optional, Set, Union

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "mygrane") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "mygrane"))

from mygrane import preferences
from interface_with_airdc import AirDCFilelistSession, get_queue_bundles, find_hub

MONTH_FOLDER_PATTERN = re.compile(r"^\d{4}\.(0[1-9]|1[0-2])$")
CANDIDATE_ROOT_DIRS = ("new releases", "new_releases", "newscans", "new scans", "new_scans", "releases", "comics")


def is_directory_item(item: Dict) -> bool:
    item_type = item.get("type")
    if isinstance(item_type, str):
        return item_type.lower() == "directory"
    if isinstance(item_type, dict):
        return (item_type.get("id") == "directory" or
                item_type.get("str", "").lower() == "directory")
    return False


def is_release_folder(name: str) -> bool:
    return name.startswith("0-Day") or name.startswith("Hitlist")


def get_release_subdir(name: str) -> str:
    if name.startswith("0-Day"):
        return "0-Days"
    if name.startswith("Hitlist"):
        return "Hitlists"
    return ""


def join_target_path(base_path: Union[str, Path], subfolder: str = "") -> str:
    base_str = str(base_path).strip()
    if not subfolder:
        if base_str and not base_str.endswith("/") and not base_str.endswith("\\"):
            base_str += "/" if ("/" in base_str or base_str.startswith("/")) else "\\"
        return base_str

    if "/" in base_str or (not "\\" in base_str and not (len(base_str) > 1 and base_str[1] == ":")):
        base_str = base_str.rstrip("/")
        sub = subfolder.strip("/")
        return f"{base_str}/{sub}/"
    else:
        base_str = base_str.rstrip("\\")
        sub = subfolder.strip("\\")
        return f"{base_str}\\{sub}\\"


def get_queued_release_names() -> Set[str]:
    queued_names = set()
    bundles = get_queue_bundles()
    for bundle in bundles:
        name = bundle.get("name")
        if name:
            queued_names.add(name)
        target = bundle.get("target")
        if target:
            target_name = Path(target).name
            if target_name:
                queued_names.add(target_name)
    return queued_names


def is_already_downloaded_or_queued(release_name: str,
                                    month_folder_name: Optional[str] = None,
                                    incoming_directory: Optional[Path] = None,
                                    input_directory: Optional[Path] = None,
                                    queued_names: Optional[Set[str]] = None) -> bool:
    queued = queued_names or set()
    if release_name in queued:
        return True

    # Note: Even if the destination folder exists locally, we still queue the download
    # so AirDC++ can fetch any new files added to the release.
    return False


def find_month_directories(session: AirDCFilelistSession, share_path: str, verbose: bool = False) -> List[Dict]:
    # Normalize share_path format
    norm_path = share_path
    if not norm_path.startswith("/"):
        norm_path = "/" + norm_path
    if not norm_path.endswith("/"):
        norm_path = norm_path + "/"

    if verbose:
        print(f"[Verbose] Searching month directories at path: '{norm_path}' (original: '{share_path}')")

    items = []
    try:
        items = session.list_directory(norm_path)
        if verbose:
            print(f"[Verbose] Items in '{norm_path}': {[i.get('name') for i in items]}")
    except Exception as e:
        if verbose:
            print(f"[Verbose] Could not list '{norm_path}': {e}. Trying root '/'...")
        if norm_path.strip("/") != "":
            try:
                items = session.list_directory("/")
                if verbose:
                    print(f"[Verbose] Items in root '/': {[i.get('name') for i in items]}")
            except Exception as e2:
                if verbose:
                    print(f"[Verbose] Could not list root '/': {e2}")
        if not items:
            raise e

    month_dirs = [item for item in items if is_directory_item(item) and MONTH_FOLDER_PATTERN.match(item.get("name", ""))]
    if month_dirs:
        if verbose:
            print(f"[Verbose] Found month directories directly in '{norm_path}': {[m.get('name') for m in month_dirs]}")
        return month_dirs

    # Check for known candidate subfolders
    for item in items:
        item_name = item.get("name", "").lower()
        if is_directory_item(item) and item_name in CANDIDATE_ROOT_DIRS:
            sub_path = item.get("path", f"{norm_path.rstrip('/')}/{item.get('name')}/")
            if verbose:
                print(f"[Verbose] Inspecting candidate subfolder '{sub_path}'...")
            try:
                sub_items = session.list_directory(sub_path)
                sub_month_dirs = [sub for sub in sub_items if is_directory_item(sub) and MONTH_FOLDER_PATTERN.match(sub.get("name", ""))]
                if sub_month_dirs:
                    if verbose:
                        print(f"[Verbose] Found month directories in candidate '{sub_path}': {[m.get('name') for m in sub_month_dirs]}")
                    return sub_month_dirs
            except Exception as e:
                if verbose:
                    print(f"[Verbose] Could not list candidate '{sub_path}': {e}")

    # If norm_path wasn't root, also check root directory
    if norm_path.strip("/") != "":
        try:
            root_items = session.list_directory("/")
            root_month_dirs = [item for item in root_items if is_directory_item(item) and MONTH_FOLDER_PATTERN.match(item.get("name", ""))]
            if root_month_dirs:
                if verbose:
                    print(f"[Verbose] Found month directories in root '/': {[m.get('name') for m in root_month_dirs]}")
                return root_month_dirs

            for item in root_items:
                item_name = item.get("name", "").lower()
                if is_directory_item(item) and item_name in CANDIDATE_ROOT_DIRS:
                    sub_path = item.get("path", f"/{item.get('name')}/")
                    if verbose:
                        print(f"[Verbose] Inspecting root candidate subfolder '{sub_path}'...")
                    try:
                        sub_items = session.list_directory(sub_path)
                        sub_month_dirs = [sub for sub in sub_items if is_directory_item(sub) and MONTH_FOLDER_PATTERN.match(sub.get("name", ""))]
                        if sub_month_dirs:
                            if verbose:
                                print(f"[Verbose] Found month directories in root candidate '{sub_path}': {[m.get('name') for m in sub_month_dirs]}")
                            return sub_month_dirs
                    except Exception as e:
                        if verbose:
                            print(f"[Verbose] Could not list root candidate '{sub_path}': {e}")
        except Exception as e:
            if verbose:
                print(f"[Verbose] Error while searching root directory: {e}")

    return month_dirs


def check_and_download_releases(target_folder: Optional[str] = None,
                                share_path: Optional[str] = None,
                                hub: Optional[Union[Dict[str, Any], str, int]] = None,
                                target_user: Optional[str] = None,
                                user_nick: Optional[str] = None,
                                share_profile: Optional[Union[int, str]] = None,
                                released_directory: Optional[Union[str, Path]] = None,
                                input_directory: Optional[Union[str, Path]] = None,
                                incoming_directory: Optional[Union[str, Path]] = None,
                                dry_run: bool = False,
                                verbose: bool = False,
                                session: Optional[AirDCFilelistSession] = None) -> List[str]:
    is_verbose = verbose or preferences.verbose

    input_dir_val = input_directory or preferences.input_directory
    input_dir_obj = Path(input_dir_val) if input_dir_val else None

    incoming_dir_val = incoming_directory or preferences.incoming_directory
    incoming_dir_obj = Path(incoming_dir_val) if incoming_dir_val else None

    # Base target path for AirDC++ (can be a remote Linux mount path like /mnt/virt/Comics/0. Released Comics/)
    air_released_base = (released_directory
                         or preferences.air_released_comics_directory
                         or (str(input_dir_obj) if input_dir_obj else None)
                         or (str(incoming_dir_obj) if incoming_dir_obj else None))

    if not air_released_base:
        raise ValueError("No destination directory configured (AIR_RELEASED_COMICS_DIRECTORY, INPUT_DIRECTORY, or INCOMING_DIRECTORY must be set).")

    # Try creating local destination directories if input_directory exists locally
    if input_dir_obj:
        try:
            if input_dir_obj.exists():
                (input_dir_obj / "0-Days").mkdir(parents=True, exist_ok=True)
                (input_dir_obj / "Hitlists").mkdir(parents=True, exist_ok=True)
        except Exception as e:
            if is_verbose:
                print(f"[Verbose] Could not create local input subdirectories: {e}")

    target_share_path = (target_folder
                         or share_path
                         or preferences.air_target_folder
                         or preferences.air_share_path
                         or "NewScans")
    target_hub = hub or preferences.air_hub
    target_user_nick = target_user or user_nick or preferences.air_target_user or preferences.air_user_nick
    target_share_profile = share_profile if share_profile is not None else preferences.air_share_profile

    if is_verbose:
        print("[Verbose] Configuration:")
        print(f"  Host: {preferences.air_host or 'http://localhost:5600'}")
        print(f"  User: {preferences.air_user or '(none)'}")
        print(f"  Target Folder / Share Path: {target_share_path}")
        print(f"  Target Hub: {target_hub or '(any/none)'}")
        print(f"  Target User: {target_user_nick or '(none)'}")
        print(f"  Share Profile: {target_share_profile or '(default)'}")
        print(f"  AirDC Released Comics Directory: {air_released_base}")
        print(f"  Local Input Directory: {input_dir_obj or '(none)'}")
        print(f"  Local Incoming Directory: {incoming_dir_obj or '(none)'}")
        print(f"  Dry Run: {dry_run}")
    else:
        if target_hub:
            print(f"Target hub: {target_hub}")
        if target_user_nick:
            print(f"Target user: {target_user_nick}")
        print(f"Downloading to: {air_released_base}")

    user_dict = {"nicks": target_user_nick} if target_user_nick else None

    queued_names = get_queued_release_names()
    if is_verbose:
        print(f"[Verbose] Currently queued bundle names ({len(queued_names)}): {sorted(list(queued_names))}")

    downloaded_or_queued_list: List[str] = []

    def process_session(sess: AirDCFilelistSession):
        month_directories = find_month_directories(sess, target_share_path, verbose=is_verbose)
        if not month_directories:
            print(f"No month directories matching YYYY.MM found in '{target_share_path}'.")
            return

        for month_item in sorted(month_directories, key=lambda x: x.get("name", "")):
            month_name = month_item.get("name")
            month_path = month_item.get("path")
            if not month_name or not month_path:
                continue

            print(f"Checking releases for month: {month_name}")
            month_contents = sess.list_directory(month_path)
            if is_verbose:
                print(f"[Verbose] Total items in month folder {month_name}: {len(month_contents)}")

            for item in month_contents:
                if not is_directory_item(item):
                    continue

                item_name = item.get("name", "")
                item_path = item.get("path", "")

                if not is_release_folder(item_name):
                    if is_verbose:
                        print(f"  [SKIPPED] Non-release item: {item_name}")
                    continue

                if is_already_downloaded_or_queued(item_name, month_name, incoming_dir_obj, input_dir_obj, queued_names):
                    print(f"  [SKIPPED] Already present/queued: {item_name}")
                    continue

                subdir = get_release_subdir(item_name)
                target_dir = join_target_path(air_released_base, subdir)

                print(f"  [QUEUEING] {item_name} -> {target_dir}")
                if not dry_run:
                    sess.download_directory(
                        remote_path=item_path,
                        target_directory=target_dir,
                        target_name=item_name
                    )
                downloaded_or_queued_list.append(item_name)
                queued_names.add(item_name)

    if session is not None:
        process_session(session)
    else:
        with AirDCFilelistSession(user=user_dict,
                                  hub=target_hub,
                                  share_profile=target_share_profile if not user_dict else None,
                                  verbose=is_verbose) as sess:
            process_session(sess)

    return downloaded_or_queued_list


def main() -> None:
    parser = argparse.ArgumentParser(description="Check AirDC++ share for new monthly releases and auto-download them.")
    parser.add_argument("--hub", type=str, default=None, help="Target hub name, URL, or ID (e.g. 'The Comic Shack')")
    parser.add_argument("--target-user", "--user-nick", dest="target_user", type=str, default=None, help="Remote target user nick (e.g. 'KT8Bot2022')")
    parser.add_argument("--target-folder", "--share-path", dest="target_folder", type=str, default=None, help="Remote target folder or share path (e.g. 'NewScans' or '/New Releases/')")
    parser.add_argument("--released-directory", "--air-released-directory", dest="released_directory", type=str, default=None, help="AirDC++ destination released comics directory (e.g. '/mnt/virt/Comics/0. Released Comics/')")
    parser.add_argument("--share-profile", type=str, default=None, help="Share profile name or ID for local share")
    parser.add_argument("--dry-run", action="store_true", help="Scan and show releases without triggering download")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose diagnostic details about API calls and matching")
    args = parser.parse_args()

    check_and_download_releases(
        target_folder=args.target_folder,
        hub=args.hub,
        target_user=args.target_user,
        share_profile=args.share_profile,
        released_directory=args.released_directory,
        dry_run=args.dry_run,
        verbose=args.verbose
    )


if __name__ == "__main__":
    main()