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
                                    month_folder_name: str,
                                    incoming_directory: Path,
                                    input_directory: Optional[Path],
                                    queued_names: Set[str]) -> bool:
    if release_name in queued_names:
        return True

    # Check incoming directory month folder
    incoming_month_dir = incoming_directory / month_folder_name
    if (incoming_month_dir / release_name).exists():
        return True

    # Check input directory destinations (moved releases)
    if input_directory and input_directory.exists():
        if (input_directory / "0-Days" / release_name).exists():
            return True
        if (input_directory / "Hitlists" / release_name).exists():
            return True
        if (input_directory / release_name).exists():
            return True

    return False


def find_month_directories(session: AirDCFilelistSession, share_path: str) -> List[Dict]:
    items = []
    try:
        items = session.list_directory(share_path)
    except Exception as e:
        if share_path.strip("/") != "":
            try:
                items = session.list_directory("/")
            except Exception:
                pass
        if not items:
            raise e

    month_dirs = [item for item in items if is_directory_item(item) and MONTH_FOLDER_PATTERN.match(item.get("name", ""))]
    if month_dirs:
        return month_dirs

    # Check for known candidate subfolders
    for item in items:
        item_name = item.get("name", "").lower()
        if is_directory_item(item) and item_name in CANDIDATE_ROOT_DIRS:
            sub_path = item.get("path", f"{share_path.rstrip('/')}/{item.get('name')}/")
            try:
                sub_items = session.list_directory(sub_path)
                sub_month_dirs = [sub for sub in sub_items if is_directory_item(sub) and MONTH_FOLDER_PATTERN.match(sub.get("name", ""))]
                if sub_month_dirs:
                    return sub_month_dirs
            except Exception:
                pass

    # If share_path wasn't root, also check root directory
    if share_path.strip("/") != "":
        try:
            root_items = session.list_directory("/")
            root_month_dirs = [item for item in root_items if is_directory_item(item) and MONTH_FOLDER_PATTERN.match(item.get("name", ""))]
            if root_month_dirs:
                return root_month_dirs

            for item in root_items:
                item_name = item.get("name", "").lower()
                if is_directory_item(item) and item_name in CANDIDATE_ROOT_DIRS:
                    sub_path = item.get("path", f"/{item.get('name')}/")
                    try:
                        sub_items = session.list_directory(sub_path)
                        sub_month_dirs = [sub for sub in sub_items if is_directory_item(sub) and MONTH_FOLDER_PATTERN.match(sub.get("name", ""))]
                        if sub_month_dirs:
                            return sub_month_dirs
                    except Exception:
                        pass
        except Exception:
            pass

    return month_dirs


def check_and_download_releases(share_path: Optional[str] = None,
                                hub: Optional[Union[Dict[str, Any], str, int]] = None,
                                target_user: Optional[str] = None,
                                user_nick: Optional[str] = None,
                                share_profile: Optional[Union[int, str]] = None,
                                dry_run: bool = False,
                                session: Optional[AirDCFilelistSession] = None) -> List[str]:
    incoming_dir_str = preferences.incoming_directory
    if not incoming_dir_str:
        raise ValueError("INCOMING_DIRECTORY preference is not set.")
    incoming_directory = Path(incoming_dir_str)
    incoming_directory.mkdir(parents=True, exist_ok=True)

    input_dir_str = preferences.input_directory
    input_directory = Path(input_dir_str) if input_dir_str else None

    target_share_path = share_path or preferences.air_share_path or "/New Releases/"
    target_hub = hub or preferences.air_hub
    target_user_nick = target_user or user_nick or preferences.air_target_user or preferences.air_user_nick
    target_share_profile = share_profile if share_profile is not None else preferences.air_share_profile

    if target_hub:
        print(f"Target hub: {target_hub}")
    if target_user_nick:
        print(f"Target user: {target_user_nick}")

    user_dict = {"nicks": target_user_nick} if target_user_nick else None

    queued_names = get_queued_release_names()
    downloaded_or_queued_list: List[str] = []

    def process_session(sess: AirDCFilelistSession):
        month_directories = find_month_directories(sess, target_share_path)
        if not month_directories:
            print(f"No month directories matching YYYY.MM found in '{target_share_path}'.")
            return

        for month_item in sorted(month_directories, key=lambda x: x.get("name", "")):
            month_name = month_item.get("name")
            month_path = month_item.get("path")
            if not month_name or not month_path:
                continue

            target_month_dir = incoming_directory / month_name
            target_month_dir.mkdir(parents=True, exist_ok=True)

            print(f"Checking releases for month: {month_name}")
            month_contents = sess.list_directory(month_path)

            for item in month_contents:
                if not is_directory_item(item):
                    continue

                item_name = item.get("name", "")
                item_path = item.get("path", "")

                if not is_release_folder(item_name):
                    continue

                if is_already_downloaded_or_queued(item_name, month_name, incoming_directory, input_directory, queued_names):
                    print(f"  [SKIPPED] Already present/queued: {item_name}")
                    continue

                print(f"  [QUEUEING] {item_name} -> {target_month_dir}")
                if not dry_run:
                    sess.download_directory(
                        remote_path=item_path,
                        target_directory=str(target_month_dir),
                        target_name=item_name
                    )
                downloaded_or_queued_list.append(item_name)
                queued_names.add(item_name)

    if session is not None:
        process_session(session)
    else:
        with AirDCFilelistSession(user=user_dict,
                                  hub=target_hub,
                                  share_profile=target_share_profile if not user_dict else None) as sess:
            process_session(sess)

    return downloaded_or_queued_list


def main() -> None:
    parser = argparse.ArgumentParser(description="Check AirDC++ share for new monthly releases and auto-download them.")
    parser.add_argument("--hub", type=str, default=None, help="Target hub name, URL, or ID (e.g. 'The Comic Shack')")
    parser.add_argument("--target-user", "--user-nick", dest="target_user", type=str, default=None, help="Remote target user nick (e.g. 'KT8Bot2022')")
    parser.add_argument("--share-path", type=str, default=None, help="Remote share path to check (e.g. '/New Releases/')")
    parser.add_argument("--share-profile", type=str, default=None, help="Share profile name or ID for local share")
    parser.add_argument("--dry-run", action="store_true", help="Scan and show releases without triggering download")
    args = parser.parse_args()

    check_and_download_releases(
        share_path=args.share_path,
        hub=args.hub,
        target_user=args.target_user,
        share_profile=args.share_profile,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()