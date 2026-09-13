import json
import os
from pathlib import Path
import time
from typing import Any, Dict, List, Optional, Union

import requests
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth

load_dotenv()


def request_to_air(endpoint: str,
                   payload: Optional[Dict[str, Any]] = None,
                   method: str = "POST",
                   params: Optional[Dict[str, Any]] = None,
                   host: Optional[str] = None,
                   user: Optional[str] = None,
                   password: Optional[str] = None) -> requests.Response:
    air_host = host or os.getenv("AIR_HOST", "http://localhost:5600")
    if not air_host.startswith("http://") and not air_host.startswith("https://"):
        air_host = f"http://{air_host}"
    air_host = air_host.rstrip("/")
    endpoint = endpoint.lstrip("/")
    url = f"{air_host}/api/v1/{endpoint}"

    air_user = user if user is not None else os.getenv('AIR_USER', '')
    air_pass = password if password is not None else os.getenv('AIR_PASS', '')
    auth = HTTPBasicAuth(air_user, air_pass) if (air_user or air_pass) else None

    headers = {'Content-Type': 'application/json'}
    data = json.dumps(payload) if payload is not None else None

    method_upper = method.upper()
    if method_upper == "GET":
        return requests.get(url, params=params, headers=headers, auth=auth)
    elif method_upper == "POST":
        return requests.post(url, data=data, params=params, headers=headers, auth=auth)
    elif method_upper == "DELETE":
        return requests.delete(url, data=data, params=params, headers=headers, auth=auth)
    elif method_upper == "PUT":
        return requests.put(url, data=data, params=params, headers=headers, auth=auth)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")


def _raise_for_status_with_detail(response: requests.Response) -> None:
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        error_detail = ""
        try:
            err_json = response.json()
            if isinstance(err_json, dict):
                error_detail = (
                    err_json.get("message")
                    or err_json.get("error")
                    or err_json.get("detail")
                    or err_json.get("description")
                    or str(err_json)
                )
            else:
                error_detail = str(err_json)
        except Exception:
            error_detail = response.text.strip() if response.text else ""

        if error_detail:
            msg = f"{e} - AirDC++ response: {error_detail}"
            raise requests.HTTPError(msg, response=response) from e
        raise e


def get_tth(filename: str) -> Optional[str]:
    try:
        response = request_to_air("share/search", payload={
            "query":
                {"pattern": filename}
        })
        response_json = response.json()
        print(response_json)
        if isinstance(response_json, list) and len(response_json) > 0:
            return response_json[0].get("tth")
        elif isinstance(response_json, dict) and "results" in response_json:
            results = response_json["results"]
            if results and len(results) > 0:
                return results[0].get("tth")
    except Exception:
        pass
    return None


def get_share_profiles() -> List[Dict[str, Any]]:
    try:
        response = request_to_air("share_profiles", method="GET")
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return data.get("profiles", data.get("items", []))
    except Exception:
        pass
    return []


def get_default_share_profile_id() -> Optional[int]:
    profiles = get_share_profiles()
    if not profiles:
        return None
    for p in profiles:
        if isinstance(p, dict) and p.get("default"):
            return p.get("id")
    if isinstance(profiles[0], dict) and "id" in profiles[0]:
        return profiles[0].get("id")
    return None


def resolve_share_profile_id(profile_identifier: Union[int, str]) -> Optional[int]:
    if isinstance(profile_identifier, int):
        return profile_identifier
    if isinstance(profile_identifier, str):
        if profile_identifier.isdigit():
            return int(profile_identifier)
        profiles = get_share_profiles()
        for p in profiles:
            if isinstance(p, dict):
                if str(p.get("id")) == profile_identifier:
                    return p.get("id")
                if str(p.get("name", "")).lower() == profile_identifier.lower():
                    return p.get("id")
    return None


def get_filelists(host: Optional[str] = None,
                  user: Optional[str] = None,
                  password: Optional[str] = None) -> List[Dict[str, Any]]:
    try:
        response = request_to_air("filelists", method="GET", host=host, user=user, password=password)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data
            elif isinstance(data, dict):
                return data.get("filelists", data.get("items", [data]))
    except Exception:
        pass
    return []


def find_hub(hub_identifier: Union[str, int],
             host: Optional[str] = None,
             user: Optional[str] = None,
             password: Optional[str] = None,
             verbose: bool = False) -> Optional[Dict[str, Any]]:
    if not hub_identifier:
        return None
    try:
        hubs = get_hubs(host=host, user=user, password=password)
    except Exception as e:
        if verbose:
            print(f"[AirDC] Failed to fetch active hubs: {e}")
        hubs = []

    hub_str = str(hub_identifier).strip()
    hub_lower = hub_str.lower()

    # Exact match on id
    for h in hubs:
        if str(h.get("id")) == hub_str:
            return h

    # Match on identity.name or name
    for h in hubs:
        identity = h.get("identity", {}) if isinstance(h.get("identity"), dict) else {}
        name = identity.get("name") or h.get("name") or ""
        if name.lower() == hub_lower:
            return h

    # Match on hub_url or identity.connect_address
    for h in hubs:
        identity = h.get("identity", {}) if isinstance(h.get("identity"), dict) else {}
        addr = identity.get("connect_address") or h.get("hub_url") or ""
        if addr.lower() == hub_lower or hub_lower in addr.lower():
            return h

    # Substring match on name
    for h in hubs:
        identity = h.get("identity", {}) if isinstance(h.get("identity"), dict) else {}
        name = identity.get("name") or h.get("name") or ""
        if hub_lower in name.lower():
            return h

    # Fallback to favorite hubs
    try:
        favs = get_favorite_hubs(host=host, user=user, password=password)
        for f in favs:
            name = f.get("name") or ""
            if name.lower() == hub_lower or str(f.get("id")) == hub_str or hub_lower in name.lower():
                return f
    except Exception as e:
        if verbose:
            print(f"[AirDC] Failed to fetch favorite hubs: {e}")

    return None


def find_user(user_identifier: Union[str, Dict[str, Any]],
              hub_identifier: Optional[Union[Dict[str, Any], str, int]] = None,
              host: Optional[str] = None,
              user: Optional[str] = None,
              password: Optional[str] = None,
              verbose: bool = False) -> Optional[Dict[str, Any]]:
    if not user_identifier:
        return None

    if isinstance(user_identifier, dict) and user_identifier.get("cid"):
        return user_identifier

    target_nick = None
    if isinstance(user_identifier, dict):
        target_nick = user_identifier.get("nicks") or user_identifier.get("nick") or user_identifier.get("name")
    else:
        target_nick = str(user_identifier).strip()

    if not target_nick:
        return None

    target_nick_lower = target_nick.lower()

    # 1. Check existing open/loaded sessions
    try:
        existing_sessions = get_filelists(host=host, user=user, password=password)
        for s in existing_sessions:
            u = s.get("user")
            if isinstance(u, dict):
                s_nick = u.get("nicks") or u.get("nick")
                s_cid = u.get("cid")
                s_hub = u.get("hub_url")
                if (s_nick and s_nick.lower() == target_nick_lower) or (s_cid and s_cid.lower() == target_nick_lower):
                    if verbose:
                        print(f"[AirDC] Found user '{target_nick}' in existing filelist session {s.get('id')} (CID: {s_cid})")
                    return {
                        "cid": s_cid,
                        "hub_url": s_hub,
                        "nicks": s_nick or target_nick,
                        "nick": s_nick or target_nick,
                        "session_id": s.get("id")
                    }
    except Exception as e:
        if verbose:
            print(f"[AirDC] Could not check existing filelist sessions: {e}")

    # 2. Check active hubs for user
    try:
        hubs = get_hubs(host=host, user=user, password=password)
    except Exception as e:
        if verbose:
            print(f"[AirDC] Could not retrieve hubs for user search: {e}")
        hubs = []

    target_hub_url = None
    if hub_identifier:
        if isinstance(hub_identifier, dict):
            target_hub_url = (hub_identifier.get("hub_url")
                              or (hub_identifier.get("identity") or {}).get("connect_address")
                              or (hub_identifier.get("identity") or {}).get("hub_url")
                              or hub_identifier.get("connect_address")
                              or hub_identifier.get("url")
                              or hub_identifier.get("address"))
        else:
            hub_info = find_hub(hub_identifier, host=host, user=user, password=password, verbose=verbose)
            if hub_info:
                target_hub_url = (hub_info.get("hub_url")
                                  or (hub_info.get("identity") or {}).get("connect_address")
                                  or (hub_info.get("identity") or {}).get("hub_url")
                                  or hub_info.get("connect_address")
                                  or hub_info.get("url")
                                  or hub_info.get("address"))
                hubs = [hub_info] + [h for h in hubs if h.get("id") != hub_info.get("id")]

    for h in hubs:
        hub_id = h.get("id")
        hub_url = (h.get("hub_url")
                   or (h.get("identity") or {}).get("connect_address")
                   or (h.get("identity") or {}).get("hub_url")
                   or h.get("connect_address")
                   or h.get("url")
                   or target_hub_url)
        if not hub_id:
            continue

        user_candidates: List[Dict[str, Any]] = []

        # Try user listing endpoints
        for ep in [f"hubs/{hub_id}/users/0/10000", f"hubs/{hub_id}/users"]:
            try:
                resp = request_to_air(ep, method="GET", host=host, user=user, password=password)
                sc = getattr(resp, "status_code", 200)
                if (sc in (200, 204)) if isinstance(sc, int) else True:
                    data = resp.json()
                    if isinstance(data, list):
                        user_candidates = data
                        break
                    elif isinstance(data, dict):
                        items = data.get("items") or data.get("users")
                        if isinstance(items, list):
                            user_candidates = items
                            break
            except Exception:
                pass

        # Try user search endpoint if list didn't succeed
        if not user_candidates:
            for ep in [f"hubs/{hub_id}/user_search", f"hubs/{hub_id}/users/search"]:
                try:
                    resp = request_to_air(ep, payload={"pattern": target_nick}, method="POST", host=host, user=user, password=password)
                    sc = getattr(resp, "status_code", 200)
                    if (sc in (200, 204)) if isinstance(sc, int) else True:
                        data = resp.json()
                        if isinstance(data, list):
                            user_candidates = data
                            break
                        elif isinstance(data, dict):
                            items = data.get("items") or data.get("users") or data.get("results")
                            if isinstance(items, list):
                                user_candidates = items
                                break
                except Exception:
                    pass

        for item in user_candidates:
            if not isinstance(item, dict):
                continue
            u_obj = item.get("user") if isinstance(item.get("user"), dict) else item
            u_nick = u_obj.get("nick") or u_obj.get("nicks") or (u_obj.get("identity") or {}).get("name") or item.get("nick") or item.get("nicks")
            u_cid = u_obj.get("cid") or item.get("cid")
            if (u_nick and str(u_nick).lower() == target_nick_lower) or (u_cid and str(u_cid).lower() == target_nick_lower):
                resolved = {
                    "cid": u_cid,
                    "hub_url": hub_url or u_obj.get("hub_url") or item.get("hub_url") or target_hub_url,
                    "nicks": u_nick or target_nick,
                    "nick": u_nick or target_nick,
                    "hub_id": hub_id
                }
                if verbose:
                    print(f"[AirDC] Resolved user '{target_nick}' in hub {hub_id}: CID={u_cid}, hub_url={resolved['hub_url']}")
                return resolved

    # 3. Global user search endpoints
    for ep in ["users/search", "users"]:
        try:
            resp = request_to_air(ep,
                                  payload={"pattern": target_nick} if "search" in ep else None,
                                  method="POST" if "search" in ep else "GET",
                                  host=host, user=user, password=password)
            sc = getattr(resp, "status_code", 200)
            if (sc in (200, 204)) if isinstance(sc, int) else True:
                data = resp.json()
                items = data if isinstance(data, list) else (data.get("items") or data.get("users") or [])
                for item in items:
                    if not isinstance(item, dict):
                        continue
                    u_obj = item.get("user") if isinstance(item.get("user"), dict) else item
                    u_nick = u_obj.get("nick") or u_obj.get("nicks") or item.get("nick")
                    u_cid = u_obj.get("cid") or item.get("cid")
                    if (u_nick and str(u_nick).lower() == target_nick_lower) or (u_cid and str(u_cid).lower() == target_nick_lower):
                        resolved = {
                            "cid": u_cid,
                            "hub_url": u_obj.get("hub_url") or item.get("hub_url") or target_hub_url,
                            "nicks": u_nick or target_nick,
                            "nick": u_nick or target_nick
                        }
                        if verbose:
                            print(f"[AirDC] Resolved user '{target_nick}' via {ep}: CID={u_cid}")
                        return resolved
        except Exception:
            pass

    return None


def create_filelist_session(user: Optional[Union[Dict[str, Any], str]] = None,
                            hub: Optional[Union[Dict[str, Any], str, int]] = None,
                            share_profile: Optional[Union[int, str]] = None,
                            timeout: int = 30,
                            host: Optional[str] = None,
                            api_user: Optional[str] = None,
                            password: Optional[str] = None,
                            verbose: bool = False) -> Union[int, str]:
    hub_url = None
    if hub is not None:
        if isinstance(hub, dict):
            hub_url = (hub.get("hub_url")
                       or (hub.get("identity") or {}).get("connect_address")
                       or (hub.get("identity") or {}).get("hub_url")
                       or hub.get("connect_address")
                       or hub.get("url")
                       or hub.get("address"))
        else:
            hub_info = find_hub(hub, host=host, user=api_user, password=password, verbose=verbose)
            if hub_info:
                hub_url = (hub_info.get("hub_url")
                           or (hub_info.get("identity") or {}).get("connect_address")
                           or (hub_info.get("identity") or {}).get("hub_url")
                           or hub_info.get("connect_address")
                           or hub_info.get("url")
                           or hub_info.get("address"))
            elif isinstance(hub, str) and (":" in hub or "." in hub):
                hub_url = hub

    target_cid = None
    target_nick = None
    resolved_hub_url = hub_url

    if user is not None:
        user_info = find_user(user, hub_identifier=hub, host=host, user=api_user, password=password, verbose=verbose)
        if user_info and user_info.get("session_id"):
            if verbose:
                print(f"[AirDC] Reusing open filelist session {user_info.get('session_id')} for user {user_info.get('nicks')}")
            return user_info.get("session_id")

        if user_info:
            target_cid = user_info.get("cid")
            target_nick = user_info.get("nicks") or user_info.get("nick")
            resolved_hub_url = user_info.get("hub_url") or hub_url
        else:
            if isinstance(user, str):
                target_nick = user
            elif isinstance(user, dict):
                target_nick = user.get("nicks") or user.get("nick") or user.get("name")
                target_cid = user.get("cid")
                if "hub_url" in user:
                    resolved_hub_url = user.get("hub_url")

    # Check if a matching filelist session is already open
    existing_sessions = get_filelists(host=host, user=api_user, password=password)
    if target_nick or target_cid:
        for s in existing_sessions:
            u = s.get("user", {})
            if isinstance(u, dict):
                s_nick = u.get("nicks") or u.get("nick")
                s_cid = u.get("cid")
                s_hub_url = u.get("hub_url")
                s_hub_urls = u.get("hub_urls", [])

                nick_match = target_nick and s_nick and str(s_nick).lower() == str(target_nick).lower()
                cid_match = target_cid and s_cid and str(s_cid).lower() == str(target_cid).lower()

                if nick_match or cid_match:
                    if resolved_hub_url:
                        if s_hub_url and s_hub_url.lower() == resolved_hub_url.lower():
                            if verbose:
                                print(f"[AirDC] Reusing existing filelist session {s.get('id')}")
                            return s.get("id")
                        if any(h.lower() == resolved_hub_url.lower() for h in s_hub_urls):
                            if verbose:
                                print(f"[AirDC] Reusing existing filelist session {s.get('id')}")
                            return s.get("id")
                    if verbose:
                        print(f"[AirDC] Reusing existing filelist session {s.get('id')}")
                    return s.get("id")

    # Build candidate payloads in priority order
    candidate_payloads: List[Dict[str, Any]] = []

    if user is not None:
        if target_cid:
            if resolved_hub_url:
                candidate_payloads.append({"user": {"cid": target_cid, "hub_url": resolved_hub_url}})
            candidate_payloads.append({"user": {"cid": target_cid}})

        if isinstance(user, dict):
            u_dict = dict(user)
            if resolved_hub_url and "hub_url" not in u_dict:
                u_dict["hub_url"] = resolved_hub_url
            if target_cid and "cid" not in u_dict:
                u_dict["cid"] = target_cid
            candidate_payloads.append({"user": u_dict})

        if target_nick:
            if resolved_hub_url:
                candidate_payloads.append({"user": {"nicks": target_nick, "hub_url": resolved_hub_url}})
                candidate_payloads.append({"user": {"nick": target_nick, "hub_url": resolved_hub_url}})
            candidate_payloads.append({"user": {"nicks": target_nick}})
            candidate_payloads.append({"user": {"nick": target_nick}})
            candidate_payloads.append({"user": {"cid": target_nick}})
            candidate_payloads.append({"user": target_nick})
    elif share_profile is not None:
        resolved_id = resolve_share_profile_id(share_profile)
        if resolved_id is not None:
            candidate_payloads.append({"share_profile": resolved_id})
        else:
            try:
                candidate_payloads.append({"share_profile": int(share_profile)})
            except (ValueError, TypeError):
                candidate_payloads.append({"share_profile": share_profile})
    else:
        default_profile_id = get_default_share_profile_id()
        if default_profile_id is not None:
            candidate_payloads.append({"share_profile": default_profile_id})
        else:
            candidate_payloads.append({"share_profile": 0})

    last_response: Optional[requests.Response] = None
    session_id: Optional[Union[int, str]] = None
    session_data: Optional[Dict[str, Any]] = None

    for payload in candidate_payloads:
        if verbose:
            print(f"[AirDC] Requesting filelist session with payload: {payload}")
        response = request_to_air("filelists", payload=payload, method="POST", host=host, user=api_user, password=password)
        last_response = response
        status_code = getattr(response, "status_code", 200)
        is_success = (status_code in (200, 201)) if isinstance(status_code, int) else True

        if is_success:
            try:
                session_data = response.json()
                session_id = session_data.get("id")
                if session_id is not None:
                    if verbose:
                        print(f"[AirDC] Filelist session created: {session_id}")
                    break
            except Exception:
                pass
        else:
            error_str = ""
            try:
                err_data = response.json()
                error_str = str(err_data)
            except Exception:
                error_str = getattr(response, "text", "") or ""

            if verbose:
                print(f"[AirDC] POST /filelists returned {status_code}: {error_str}")

            if "already open" in error_str.lower():
                latest_sessions = get_filelists(host=host, user=api_user, password=password)
                if target_nick:
                    for s in latest_sessions:
                        u = s.get("user", {})
                        if isinstance(u, dict) and (u.get("nicks") or u.get("nick") or "").lower() == str(target_nick).lower():
                            return s.get("id")
                if latest_sessions:
                    return latest_sessions[0].get("id")

    if session_id is None:
        if last_response is not None:
            _raise_for_status_with_detail(last_response)
        raise RuntimeError("Failed to create filelist session: all candidate payloads failed.")

    start_time = time.time()
    state = (session_data or {}).get("state", {})
    state_id = state.get("id") if isinstance(state, dict) else state

    while state_id not in ("loaded", "downloaded", "ready") and (time.time() - start_time) < timeout:
        if state_id in ("failed", "error"):
            raise RuntimeError(f"Failed to load filelist session {session_id}: {session_data}")
        if verbose:
            print(f"[AirDC] Waiting for filelist session {session_id} to load (current state: {state_id})...")
        time.sleep(0.5)
        status_data = get_filelist_status(session_id, host=host, user=api_user, password=password)
        state = status_data.get("state", {})
        state_id = state.get("id") if isinstance(state, dict) else state

    if verbose:
        print(f"[AirDC] Filelist session {session_id} is ready (state: {state_id}).")

    return session_id


def get_filelist_status(session_id: Union[int, str],
                        host: Optional[str] = None,
                        user: Optional[str] = None,
                        password: Optional[str] = None) -> Dict[str, Any]:
    response = request_to_air(f"filelists/{session_id}", method="GET", host=host, user=user, password=password)
    _raise_for_status_with_detail(response)
    return response.json()


def list_filelist_directory(session_id: Union[int, str],
                            path: str,
                            host: Optional[str] = None,
                            user: Optional[str] = None,
                            password: Optional[str] = None,
                            timeout: int = 15) -> List[Dict[str, Any]]:
    # Normalize path to ensure leading and trailing forward slashes
    if not path.startswith("/"):
        path = "/" + path
    if not path.endswith("/"):
        path = path + "/"

    try:
        response = request_to_air(f"filelists/{session_id}/directory",
                                  payload={"list_path": path},
                                  method="POST",
                                  host=host, user=user, password=password)
    except Exception:
        response = request_to_air(f"filelists/{session_id}/directory",
                                  payload={"path": path},
                                  method="POST",
                                  host=host, user=user, password=password)

    status_code = getattr(response, "status_code", 200)
    if not isinstance(status_code, int) or status_code in (200, 204):
        try:
            data = response.json()
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                items = data.get("items") or data.get("children") or data.get("directories")
                if isinstance(items, list):
                    return items
        except Exception:
            pass

    start_time = time.time()
    while time.time() - start_time < timeout:
        items_resp = request_to_air(f"filelists/{session_id}/items/0/10000",
                                    method="GET",
                                    host=host, user=user, password=password)
        items_status = getattr(items_resp, "status_code", 200)
        if not isinstance(items_status, int) or items_status in (200, 204):
            try:
                data = items_resp.json()
                if isinstance(data, dict) and "items" in data:
                    return data["items"]
                if isinstance(data, list):
                    return data
            except Exception:
                pass
        time.sleep(0.5)

    return []


def create_directory_download(list_path: str,
                              target_name: Optional[str] = None,
                              user: Optional[Union[Dict[str, Any], str]] = None,
                              hub_url: Optional[str] = None,
                              cid: Optional[str] = None,
                              target_directory: Optional[Union[str, Path]] = None,
                              log_bundle_errors: bool = True,
                              priority: Optional[int] = None,
                              host: Optional[str] = None,
                              api_user: Optional[str] = None,
                              password: Optional[str] = None,
                              verbose: bool = False) -> Dict[str, Any]:
    """
    Queue a directory download from a remote user's filelist share via:
    POST /api/v1/filelists/directory_downloads

    Request Attributes:
    - user: { "cid": "<CID>", "hub_url": "<HUB_URL>" }
    - list_path: Directory path in the filelist (e.g. "/NewScans/2024.01/0-Day - 2024-01-03/")
    - target_name: Bundle/directory target name (e.g. "0-Day - 2024-01-03")
    - target_directory: Destination path on the filesystem (optional)
    - log_bundle_errors: Whether to show bundle creation errors in event log (optional, default True)
    - priority: Download priority (optional)
    """
    norm_path = list_path
    if not norm_path.startswith("/"):
        norm_path = "/" + norm_path
    if not norm_path.endswith("/"):
        norm_path = norm_path + "/"

    if not target_name:
        parts = [p for p in norm_path.split("/") if p]
        target_name = parts[-1] if parts else "download"

    user_cid = cid
    user_hub_url = hub_url

    if isinstance(user, dict):
        user_cid = user_cid or user.get("cid")
        user_hub_url = user_hub_url or user.get("hub_url") or (user.get("identity") or {}).get("connect_address")
        if not user_hub_url and user.get("hub_urls"):
            user_hub_url = user.get("hub_urls")[0]
    elif isinstance(user, str):
        if len(user) == 39 and user.isalnum():
            user_cid = user_cid or user
        else:
            resolved_user = find_user(user, host=host, user=api_user, password=password, verbose=verbose)
            if resolved_user:
                user_cid = user_cid or resolved_user.get("cid")
                user_hub_url = user_hub_url or resolved_user.get("hub_url")

    if not user_hub_url:
        try:
            hubs = get_hubs(host=host, user=api_user, password=password)
            if hubs:
                user_hub_url = (hubs[0].get("hub_url")
                                or (hubs[0].get("identity") or {}).get("connect_address")
                                or (hubs[0].get("identity") or {}).get("hub_url")
                                or hubs[0].get("connect_address")
                                or hubs[0].get("url")
                                or hubs[0].get("address"))
        except Exception:
            pass

    if not user_cid or not user_hub_url:
        try:
            filelists = get_filelists(host=host, user=api_user, password=password)
            for fl in filelists:
                fl_user = fl.get("user") or {}
                if isinstance(fl_user, dict):
                    if not user_cid:
                        user_cid = fl_user.get("cid")
                    if not user_hub_url:
                        user_hub_url = fl_user.get("hub_url") or (fl_user.get("hub_urls") or [None])[0]
                    if user_cid and user_hub_url:
                        break
        except Exception:
            pass

    user_payload: Dict[str, Any] = {}
    if user_cid:
        user_payload["cid"] = user_cid
    if user_hub_url:
        user_payload["hub_url"] = user_hub_url

    payload: Dict[str, Any] = {
        "user": user_payload,
        "list_path": norm_path,
        "target_name": target_name,
        "log_bundle_errors": log_bundle_errors
    }
    if target_directory is not None:
        payload["target_directory"] = str(target_directory)
    if priority is not None:
        payload["priority"] = priority

    if verbose:
        print(f"[AirDC] Creating directory download: POST /api/v1/filelists/directory_downloads with payload: {payload}")

    response = request_to_air("filelists/directory_downloads",
                              payload=payload,
                              method="POST",
                              host=host, user=api_user, password=password)
    _raise_for_status_with_detail(response)
    if response.content:
        try:
            return response.json()
        except Exception:
            return {"status": "ok", "status_code": getattr(response, "status_code", 200)}
    return {"status": "ok", "status_code": getattr(response, "status_code", 200)}


def download_filelist_directory(session_id: Union[int, str],
                                remote_path: str,
                                target_directory: Optional[Union[str, Path]] = None,
                                target_name: Optional[str] = None,
                                priority: int = 0,
                                user_info: Optional[Dict[str, Any]] = None,
                                log_bundle_errors: bool = True,
                                host: Optional[str] = None,
                                user: Optional[str] = None,
                                password: Optional[str] = None,
                                verbose: bool = False) -> Dict[str, Any]:
    norm_path = remote_path
    if not norm_path.startswith("/"):
        norm_path = "/" + norm_path
    if not norm_path.endswith("/"):
        norm_path = norm_path + "/"

    if not target_name:
        parts = [p for p in norm_path.split("/") if p]
        target_name = parts[-1] if parts else "download"

    # 1. First attempt: Use POST /api/v1/filelists/directory_downloads
    resolved_user = dict(user_info) if isinstance(user_info, dict) else {}
    if not resolved_user or "cid" not in resolved_user or "hub_url" not in resolved_user:
        try:
            status_data = get_filelist_status(session_id, host=host, user=user, password=password)
            if isinstance(status_data, dict) and isinstance(status_data.get("user"), dict):
                for k, v in status_data["user"].items():
                    if k not in resolved_user or not resolved_user[k]:
                        resolved_user[k] = v
        except Exception:
            pass

    if "cid" not in resolved_user and isinstance(session_id, str) and len(session_id) == 39 and session_id.isalnum():
        resolved_user["cid"] = session_id

    try:
        return create_directory_download(list_path=norm_path,
                                         target_name=target_name,
                                         user=resolved_user,
                                         target_directory=str(target_directory) if target_directory is not None else None,
                                         log_bundle_errors=log_bundle_errors,
                                         priority=priority if priority != 0 else None,
                                         host=host,
                                         api_user=user,
                                         password=password,
                                         verbose=verbose)
    except requests.HTTPError as e:
        if verbose:
            status = e.response.status_code if e.response is not None else "error"
            print(f"[AirDC] POST /api/v1/filelists/directory_downloads failed with HTTP {status}: {e}. Trying fallback endpoints...")
        if e.response is None or e.response.status_code not in (400, 404, 405, 422):
            raise
    except Exception as e:
        if verbose:
            print(f"[AirDC] POST /api/v1/filelists/directory_downloads failed: {e}. Trying fallback endpoints...")

    # 2. Fallback attempts for alternative/legacy API versions
    full_payload: Dict[str, Any] = {
        "path": norm_path,
        "list_path": norm_path,
        "priority": priority
    }
    if target_directory is not None:
        full_payload["target_directory"] = str(target_directory)
    if target_name is not None:
        full_payload["target_name"] = target_name

    basic_payload: Dict[str, Any] = {
        "path": norm_path
    }
    if target_directory is not None:
        basic_payload["target_directory"] = str(target_directory)
    if target_name is not None:
        basic_payload["target_name"] = target_name

    candidate_endpoints = [
        f"filelists/{session_id}/directory_downloads",
        f"filelists/{session_id}/download",
        f"filelists/{session_id}/directory/download",
        f"filelists/{session_id}/download_directory"
    ]
    candidate_payloads = [full_payload, basic_payload]

    last_error = None
    for endpoint in candidate_endpoints:
        for payload in candidate_payloads:
            try:
                if verbose:
                    print(f"[AirDC] Attempting fallback download: POST /api/v1/{endpoint} with payload {payload}")
                response = request_to_air(endpoint,
                                          payload=payload,
                                          method="POST",
                                          host=host, user=user, password=password)
                _raise_for_status_with_detail(response)
                if response.content:
                    try:
                        return response.json()
                    except Exception:
                        return {"status": "ok", "status_code": getattr(response, "status_code", 200)}
                return {"status": "ok", "status_code": getattr(response, "status_code", 200)}
            except requests.HTTPError as e:
                last_error = e
                if verbose:
                    status = e.response.status_code if e.response is not None else "error"
                    print(f"[AirDC] POST /api/v1/{endpoint} failed with HTTP {status}: {e}")
                if e.response is not None and e.response.status_code in (400, 404, 405, 422):
                    continue
                raise
            except Exception as e:
                last_error = e
                if verbose:
                    print(f"[AirDC] POST /api/v1/{endpoint} failed: {e}")
                continue

    if last_error:
        raise last_error
    raise RuntimeError(f"Failed to queue download for '{norm_path}' in session {session_id}")


def close_filelist_session(session_id: Union[int, str],
                           host: Optional[str] = None,
                           user: Optional[str] = None,
                           password: Optional[str] = None) -> bool:
    try:
        response = request_to_air(f"filelists/{session_id}", method="DELETE", host=host, user=user, password=password)
        return response.status_code in (200, 204, 404)
    except Exception:
        return False


def get_queue_bundles() -> List[Dict[str, Any]]:
    try:
        response = request_to_air("queue/bundles", method="GET")
        _raise_for_status_with_detail(response)
        data = response.json()
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            return data.get("bundles", data.get("items", []))
    except Exception:
        pass
    return []


def get_hubs(host: Optional[str] = None,
             user: Optional[str] = None,
             password: Optional[str] = None) -> List[Dict[str, Any]]:
    response = request_to_air("hubs", method="GET", host=host, user=user, password=password)
    _raise_for_status_with_detail(response)
    data = response.json()
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return data.get("hubs", data.get("items", [data]))
    return []


def get_favorite_hubs(host: Optional[str] = None,
                       user: Optional[str] = None,
                       password: Optional[str] = None) -> List[Dict[str, Any]]:
    response = request_to_air("favorite_hubs", method="GET", host=host, user=user, password=password)
    _raise_for_status_with_detail(response)
    data = response.json()
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return data.get("hubs", data.get("items", [data]))
    return []


class AirDCFilelistSession:
    """Context manager for managing the lifecycle of an AirDC++ filelist session."""

    def __init__(self,
                 user: Optional[Union[Dict[str, Any], str]] = None,
                 hub: Optional[Union[Dict[str, Any], str, int]] = None,
                 share_profile: Optional[Union[int, str]] = None,
                 timeout: int = 30,
                 host: Optional[str] = None,
                 api_user: Optional[str] = None,
                 password: Optional[str] = None,
                 verbose: bool = False):
        self.user = user
        self.hub = hub
        self.share_profile = share_profile
        self.timeout = timeout
        self.host = host
        self.api_user = api_user
        self.password = password
        self.verbose = verbose
        self.session_id: Optional[Union[int, str]] = None
        self.user_info: Optional[Dict[str, Any]] = None

    def __enter__(self) -> "AirDCFilelistSession":
        self.session_id = create_filelist_session(user=self.user,
                                                  hub=self.hub,
                                                  share_profile=self.share_profile,
                                                  timeout=self.timeout,
                                                  host=self.host,
                                                  api_user=self.api_user,
                                                  password=self.password,
                                                  verbose=self.verbose)
        try:
            status = get_filelist_status(self.session_id, host=self.host, user=self.api_user, password=self.password)
            if isinstance(status, dict) and isinstance(status.get("user"), dict):
                self.user_info = status["user"]
        except Exception:
            pass

        if not self.user_info and isinstance(self.user, dict):
            self.user_info = self.user

        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.session_id is not None:
            close_filelist_session(self.session_id,
                                   host=self.host,
                                   user=self.api_user,
                                   password=self.password)
            self.session_id = None

    def list_directory(self, path: str, timeout: int = 15) -> List[Dict[str, Any]]:
        if self.session_id is None:
            raise RuntimeError("Filelist session is not open.")
        return list_filelist_directory(self.session_id, path,
                                       host=self.host,
                                       user=self.api_user,
                                       password=self.password,
                                       timeout=timeout)

    def download_directory(self,
                           remote_path: str,
                           target_directory: Optional[Union[str, Path]] = None,
                           target_name: Optional[str] = None,
                           priority: int = 0,
                           log_bundle_errors: bool = True) -> Dict[str, Any]:
        if self.session_id is None:
            raise RuntimeError("Filelist session is not open.")
        return download_filelist_directory(self.session_id,
                                           remote_path=remote_path,
                                           target_directory=target_directory,
                                           target_name=target_name,
                                           priority=priority,
                                           user_info=self.user_info,
                                           log_bundle_errors=log_bundle_errors,
                                           host=self.host,
                                           user=self.api_user,
                                           password=self.password,
                                           verbose=self.verbose)


if __name__ == "__main__":
    import argparse
    from pprint import pprint

    parser = argparse.ArgumentParser(description="AirDC++ interface utilities")
    parser.add_argument("--hubs", action="store_true", help="List active hub sessions")
    parser.add_argument("--favorites", action="store_true", help="List favorite hubs")
    parser.add_argument("--tth", type=str, default=None, help="Search TTH for filename")
    args = parser.parse_args()

    if args.hubs:
        pprint(get_hubs())
    elif args.favorites:
        pprint(get_favorite_hubs())
    elif args.tth:
        print(get_tth(args.tth))
    else:
        print("Connected hubs:")
        pprint(get_hubs())
