from datetime import date
from pathlib import Path
import re
import shutil
import sys

from mygrane import preferences

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "mygrane"))


MONTH_FOLDER_PATTERN = re.compile(r"^\d{4}\.(0[1-9]|1[0-2])$")


def is_before_this_month(folder_name: str) -> bool:
    year_text, month_text = folder_name.split(".")
    folder_year = int(year_text)
    folder_month = int(month_text)

    today = date.today()

    return (folder_year, folder_month) < (today.year, today.month)


def move_folders_starting_with(source_month_folder: Path, folder_prefix: str, destination_root: Path) -> None:
    destination_root.mkdir(parents=True, exist_ok=True)

    for source_folder in source_month_folder.iterdir():
        if not source_folder.is_dir():
            continue

        if not source_folder.name.startswith(folder_prefix):
            continue

        destination_folder = destination_root / source_folder.name

        if destination_folder.exists():
            print(f"Skipping, destination already exists: {destination_folder}")
            continue

        print(f"Moving: {source_folder} -> {destination_folder}")
        shutil.move(str(source_folder), str(destination_folder))


def main() -> None:
    incoming_directory = Path(preferences.incoming_directory)
    input_directory = Path(preferences.input_directory)

    zero_day_destination = input_directory / "0-Days"
    hitlist_destination = input_directory / "Hitlists"

    if not incoming_directory.exists():
        raise FileNotFoundError(f"Incoming directory does not exist: {incoming_directory}")

    for folder in incoming_directory.iterdir():
        if not folder.is_dir():
            continue

        if not MONTH_FOLDER_PATTERN.match(folder.name):
            continue

        if not is_before_this_month(folder.name):
            continue

        move_folders_starting_with(folder, "0-Day", zero_day_destination)
        move_folders_starting_with(folder, "Hitlist", hitlist_destination)


if __name__ == "__main__":
    main()