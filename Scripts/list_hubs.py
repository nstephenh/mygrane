import argparse
import json
import os
from pathlib import Path
import sys
from typing import Any, Dict, List, Union

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "mygrane") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "mygrane"))

from mygrane import preferences
from interface_with_airdc import get_hubs, get_favorite_hubs


def format_bytes(byte_count: Union[int, float]) -> str:
    if not isinstance(byte_count, (int, float)) or byte_count <= 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0
    val = float(byte_count)
    while val >= 1024 and unit_index < len(units) - 1:
        val /= 1024
        unit_index += 1
    return f"{val:.2f} {units[unit_index]}"


def print_hubs_summary(hubs: List[Dict[str, Any]]) -> None:
    if not hubs:
        print("No active hub sessions found in AirDC++.")
        return

    print(f"Found {len(hubs)} hub session(s):")
    print("=" * 60)
    for idx, hub in enumerate(hubs, start=1):
        hub_id = hub.get("id", "Unknown")
        identity = hub.get("identity", {}) if isinstance(hub.get("identity"), dict) else {}
        name = identity.get("name") or hub.get("name") or "Unnamed Hub"
        description = identity.get("description") or hub.get("description") or ""
        address = identity.get("connect_address") or hub.get("hub_url") or hub.get("address") or "N/A"

        connect_state = hub.get("connect_state", {})
        if isinstance(connect_state, dict):
            status = connect_state.get("str") or connect_state.get("id") or "Unknown"
        else:
            status = str(connect_state or "Unknown")

        user_info = hub.get("user", {}) if isinstance(hub.get("user"), dict) else {}
        nick = user_info.get("nicks") or hub.get("nick") or preferences.air_user_nick or "N/A"

        counts = hub.get("counts", {}) if isinstance(hub.get("counts"), dict) else {}
        user_count = counts.get("users") or hub.get("users")

        share_bytes = counts.get("share_size") or hub.get("share_size")

        print(f"[{idx}] ID: {hub_id} | Name: {name}")
        print(f"    Status:      {status}")
        print(f"    Address:     {address}")
        if description:
            print(f"    Description: {description}")
        print(f"    Nick:        {nick}")
        if user_count is not None:
            print(f"    Users:       {user_count}")
        if share_bytes is not None:
            print(f"    Share Size:  {format_bytes(share_bytes)}")
        print("-" * 60)


def main() -> None:
    parser = argparse.ArgumentParser(description="Test and list AirDC++ hubs.")
    parser.add_argument("--host", type=str, default=None, help="AirDC++ host (e.g. '10.0.1.125:5600')")
    parser.add_argument("--user", type=str, default=None, help="AirDC++ API username")
    parser.add_argument("--password", type=str, default=None, help="AirDC++ API password")
    parser.add_argument("--json", action="store_true", help="Output raw JSON response")
    parser.add_argument("--favorites", action="store_true", help="List favorite hubs instead of active hub sessions")
    args = parser.parse_args()

    host = args.host or preferences.air_host or os.getenv("AIR_HOST", "http://localhost:5600")
    user = args.user if args.user is not None else (preferences.air_user or os.getenv("AIR_USER", ""))
    password = args.password if args.password is not None else (preferences.air_pass or os.getenv("AIR_PASS", ""))

    print(f"Querying AirDC++ at {host} ...")
    try:
        if args.favorites:
            hubs = get_favorite_hubs(host=host, user=user, password=password)
        else:
            hubs = get_hubs(host=host, user=user, password=password)
    except Exception as e:
        print(f"\n[ERROR] Failed to query hubs from AirDC++: {e}", file=sys.stderr)
        print("Please verify that AirDC++ is running and that your AIR_HOST, AIR_USER, and AIR_PASS settings in .env are correct.", file=sys.stderr)
        sys.exit(1)

    if args.json:
        print(json.dumps(hubs, indent=2))
    else:
        print_hubs_summary(hubs)


if __name__ == "__main__":
    main()
