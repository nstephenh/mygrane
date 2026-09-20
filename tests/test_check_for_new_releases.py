import unittest
from unittest.mock import MagicMock, patch
from pathlib import Path
import tempfile
import shutil
import requests

from interface_with_airdc import (
    request_to_air,
    create_filelist_session,
    list_filelist_directory,
    download_filelist_directory,
    create_directory_download,
    close_filelist_session,
    get_queue_bundles,
    get_share_profiles,
    get_default_share_profile_id,
    resolve_share_profile_id,
    get_filelists,
    find_hub,
    _raise_for_status_with_detail,
    AirDCFilelistSession,
)
from Scripts.check_for_new_releases import (
    is_directory_item,
    is_release_folder,
    get_release_subdir,
    join_target_path,
    is_already_downloaded_or_queued,
    find_month_directories,
    check_and_download_releases,
)


class TestAirDCInterface(unittest.TestCase):

    @patch("interface_with_airdc.requests.post")
    def test_request_to_air_post(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 1, "state": {"id": "loaded"}}
        mock_post.return_value = mock_response

        res = request_to_air("filelists", payload={"share_profile": 0}, host="http://127.0.0.1:5600", user="u", password="p")
        self.assertEqual(res, mock_response)
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], "http://127.0.0.1:5600/api/v1/filelists")

    @patch("interface_with_airdc.requests.get")
    def test_request_to_air_get(self, mock_get):
        mock_response = MagicMock()
        mock_response.json.return_value = [{"id": 1, "name": "bundle1"}]
        mock_get.return_value = mock_response

        res = request_to_air("queue/bundles", method="GET", host="http://127.0.0.1:5600")
        self.assertEqual(res, mock_response)
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        self.assertEqual(args[0], "http://127.0.0.1:5600/api/v1/queue/bundles")

    @patch("interface_with_airdc.request_to_air")
    def test_create_filelist_session(self, mock_req):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 42, "state": {"id": "loaded"}}
        mock_response.raise_for_status.return_value = None
        mock_req.return_value = mock_response

        session_id = create_filelist_session(share_profile=0)
        self.assertEqual(session_id, 42)

    @patch("interface_with_airdc.request_to_air")
    def test_create_filelist_session_with_user_string(self, mock_req):
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 10, "state": {"id": "loaded"}}
        mock_response.raise_for_status.return_value = None
        mock_req.return_value = mock_response

        session_id = create_filelist_session(user="Alice")
        self.assertEqual(session_id, 10)
        mock_req.assert_called_with("filelists", payload={"user": {"nicks": "Alice"}}, method="POST", host=None, user=None, password=None)

    @patch("interface_with_airdc.find_hub")
    @patch("interface_with_airdc.request_to_air")
    def test_create_filelist_session_with_hub_and_user(self, mock_req, mock_find_hub):
        mock_find_hub.return_value = {
            "id": 1,
            "identity": {"name": "The Comic Shack", "connect_address": "One.comicshack.org:411"},
            "hub_url": "One.comicshack.org:411"
        }
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 15, "state": {"id": "loaded"}}
        mock_response.raise_for_status.return_value = None
        mock_req.return_value = mock_response

        session_id = create_filelist_session(user="KT8Bot2022", hub="The Comic Shack")
        self.assertEqual(session_id, 15)
        mock_req.assert_called_with(
            "filelists",
            payload={"user": {"nicks": "KT8Bot2022", "hub_url": "One.comicshack.org:411"}},
            method="POST",
            host=None,
            user=None,
            password=None
        )

    @patch("interface_with_airdc.get_filelists")
    def test_create_filelist_session_reuse_existing(self, mock_get_filelists):
        mock_get_filelists.return_value = [
            {
                "id": "OPEN_SESSION_123",
                "user": {"nicks": "KT8Bot2022", "hub_url": "One.comicshack.org:411"}
            }
        ]
        session_id = create_filelist_session(user="KT8Bot2022", hub="One.comicshack.org:411")
        self.assertEqual(session_id, "OPEN_SESSION_123")

    @patch("interface_with_airdc.get_hubs")
    def test_find_hub_by_name_and_id(self, mock_get_hubs):
        mock_get_hubs.return_value = [
            {"id": 1, "identity": {"name": "The Comic Shack"}, "hub_url": "One.comicshack.org:411"},
            {"id": 2, "identity": {"name": "Perfection"}, "hub_url": "Perfection.comichub.org:777"}
        ]
        hub = find_hub("The Comic Shack")
        self.assertIsNotNone(hub)
        self.assertEqual(hub["id"], 1)

        hub_by_id = find_hub(2)
        self.assertIsNotNone(hub_by_id)
        self.assertEqual(hub_by_id["identity"]["name"], "Perfection")

        hub_by_url = find_hub("One.comicshack.org:411")
        self.assertIsNotNone(hub_by_url)
        self.assertEqual(hub_by_url["id"], 1)

    @patch("interface_with_airdc.get_share_profiles")
    @patch("interface_with_airdc.request_to_air")
    def test_create_filelist_session_auto_discover_profile(self, mock_req, mock_profiles):
        mock_profiles.return_value = [{"id": 1, "name": "Default", "default": True}]
        mock_response = MagicMock()
        mock_response.json.return_value = {"id": 20, "state": {"id": "loaded"}}
        mock_response.raise_for_status.return_value = None
        mock_req.return_value = mock_response

        session_id = create_filelist_session()
        self.assertEqual(session_id, 20)
        mock_req.assert_called_with("filelists", payload={"share_profile": 1}, method="POST", host=None, user=None, password=None)

    @patch("interface_with_airdc.get_share_profiles")
    def test_resolve_share_profile_id(self, mock_profiles):
        mock_profiles.return_value = [
            {"id": 1, "name": "Default", "default": False},
            {"id": 2, "name": "Comics", "default": True}
        ]
        self.assertEqual(resolve_share_profile_id("Comics"), 2)
        self.assertEqual(resolve_share_profile_id("comics"), 2)
        self.assertEqual(resolve_share_profile_id("1"), 1)
        self.assertEqual(resolve_share_profile_id(2), 2)
        self.assertEqual(get_default_share_profile_id(), 2)

    def test_raise_for_status_with_detail(self):
        import requests
        mock_response = MagicMock()
        mock_response.status_code = 422
        mock_response.url = "http://127.0.0.1:5600/api/v1/filelists"
        mock_response.json.return_value = {"message": "Share profile not found"}
        mock_response.raise_for_status.side_effect = requests.HTTPError("422 Client Error: Unknown", response=mock_response)

        with self.assertRaises(requests.HTTPError) as ctx:
            _raise_for_status_with_detail(mock_response)
        self.assertIn("Share profile not found", str(ctx.exception))

    @patch("interface_with_airdc.request_to_air")
    def test_list_filelist_directory(self, mock_req):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"name": "2024.01", "type": {"id": "directory"}, "path": "/New Releases/2024.01/"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_req.return_value = mock_response

        items = list_filelist_directory(42, "/New Releases/")
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["name"], "2024.01")

    @patch("interface_with_airdc.request_to_air")
    def test_create_directory_download(self, mock_req):
        mock_response = MagicMock()
        mock_response.json.return_value = {"bundle_id": 100}
        mock_response.raise_for_status.return_value = None
        mock_req.return_value = mock_response

        res = create_directory_download(
            list_path="/NewScans/2024.01/0-Day - 2024-01-03/",
            target_name="0-Day - 2024-01-03",
            user={"cid": "NJSHVYR4ZHCZFUEZNGA7M2D72S5AB4WQAMPBKFA", "hub_url": "adcs://myhub.com:6423"},
            target_directory="C:/Incoming/2024.01",
            log_bundle_errors=True
        )
        self.assertEqual(res, {"bundle_id": 100})
        mock_req.assert_called_with(
            "filelists/directory_downloads",
            payload={
                "user": {
                    "cid": "NJSHVYR4ZHCZFUEZNGA7M2D72S5AB4WQAMPBKFA",
                    "hub_url": "adcs://myhub.com:6423"
                },
                "list_path": "/NewScans/2024.01/0-Day - 2024-01-03/",
                "target_name": "0-Day - 2024-01-03",
                "log_bundle_errors": True,
                "target_directory": "C:/Incoming/2024.01/"
            },
            method="POST",
            host=None,
            user=None,
            password=None
        )

    @patch("interface_with_airdc.get_hubs")
    @patch("interface_with_airdc.request_to_air")
    def test_create_directory_download_with_cid_and_hub_lookup(self, mock_req, mock_get_hubs):
        mock_get_hubs.return_value = [{"id": 1, "hub_url": "adcs://myhub.com:6423"}]
        mock_response = MagicMock()
        mock_response.json.return_value = {"bundle_id": 101}
        mock_response.raise_for_status.return_value = None
        mock_req.return_value = mock_response

        res = create_directory_download(
            list_path="/Share/Ubuntu/",
            target_name="Ubuntu",
            cid="NJSHVYR4ZHCZFUEZNGA7M2D72S5AB4WQAMPBKFA"
        )
        self.assertEqual(res, {"bundle_id": 101})
        mock_req.assert_called_with(
            "filelists/directory_downloads",
            payload={
                "user": {
                    "cid": "NJSHVYR4ZHCZFUEZNGA7M2D72S5AB4WQAMPBKFA",
                    "hub_url": "adcs://myhub.com:6423"
                },
                "list_path": "/Share/Ubuntu/",
                "target_name": "Ubuntu",
                "log_bundle_errors": True
            },
            method="POST",
            host=None,
            user=None,
            password=None
        )

    @patch("interface_with_airdc.request_to_air")
    def test_download_filelist_directory(self, mock_req):
        mock_response = MagicMock()
        mock_response.json.return_value = {"bundle_id": 100}
        mock_response.raise_for_status.return_value = None
        mock_req.return_value = mock_response

        res = download_filelist_directory(
            "SMNF3MD2ERR2WGASZU7MKV3KNSBVIJYCJ75IHPQ",
            "/New Releases/2024.01/0-Day - 2024-01-01/",
            "C:/Incoming/2024.01",
            "0-Day - 2024-01-01",
            user_info={"cid": "SMNF3MD2ERR2WGASZU7MKV3KNSBVIJYCJ75IHPQ", "hub_url": "adcs://myhub.com:6423"}
        )
        self.assertEqual(res, {"bundle_id": 100})
        self.assertEqual(mock_req.call_args[0][0], "filelists/directory_downloads")
        self.assertEqual(mock_req.call_args[1]["payload"]["user"]["cid"], "SMNF3MD2ERR2WGASZU7MKV3KNSBVIJYCJ75IHPQ")
        self.assertEqual(mock_req.call_args[1]["payload"]["target_name"], "0-Day - 2024-01-01")

    @patch("interface_with_airdc.request_to_air")
    def test_download_filelist_directory_fallback_on_400(self, mock_req):
        err_response = MagicMock()
        err_response.status_code = 400
        err_response.json.return_value = {"message": "Invalid field: priority"}
        err = requests.HTTPError(response=err_response)

        ok_response = MagicMock()
        ok_response.status_code = 200
        ok_response.json.return_value = {"bundle_id": 200}
        ok_response.raise_for_status.return_value = None

        mock_req.side_effect = [err, ok_response]

        res = download_filelist_directory(
            42,
            "/NewScans/2024.01/0-Day - 2024-01-01/",
            "C:/Incoming/2024.01",
            "0-Day - 2024-01-01",
            user_info={"cid": "SMNF3MD2ERR2WGASZU7MKV3KNSBVIJYCJ75IHPQ", "hub_url": "adcs://myhub.com:6423"}
        )
        self.assertEqual(res, {"bundle_id": 200})
        self.assertEqual(mock_req.call_count, 2)

    @patch("interface_with_airdc.request_to_air")
    def test_download_filelist_directory_204_no_content(self, mock_req):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_response.content = b""
        mock_response.raise_for_status.return_value = None
        mock_req.return_value = mock_response

        res = download_filelist_directory(
            42,
            "/NewScans/2024.01/0-Day - 2024-01-01/",
            "C:/Incoming/2024.01",
            user_info={"cid": "SMNF3MD2ERR2WGASZU7MKV3KNSBVIJYCJ75IHPQ", "hub_url": "adcs://myhub.com:6423"}
        )
        self.assertEqual(res, {"status": "ok", "status_code": 204})

    @patch("interface_with_airdc.request_to_air")
    def test_close_filelist_session(self, mock_req):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_req.return_value = mock_response

        success = close_filelist_session(42)
        self.assertTrue(success)


class TestCheckForNewReleases(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.incoming_dir = Path(self.temp_dir) / "incoming"
        self.input_dir = Path(self.temp_dir) / "input"
        self.incoming_dir.mkdir(parents=True)
        self.input_dir.mkdir(parents=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_is_directory_item(self):
        self.assertTrue(is_directory_item({"type": "directory"}))
        self.assertTrue(is_directory_item({"type": {"id": "directory"}}))
        self.assertTrue(is_directory_item({"type": {"str": "Directory"}}))
        self.assertFalse(is_directory_item({"type": "file"}))
        self.assertFalse(is_directory_item({"type": {"id": "file"}}))

    def test_get_release_subdir(self):
        self.assertEqual(get_release_subdir("0-Day - 2024-01-03"), "0-Days")
        self.assertEqual(get_release_subdir("0-Day Week of 2026.09.07"), "0-Days")
        self.assertEqual(get_release_subdir("Hitlist - 2024-01-03"), "Hitlists")
        self.assertEqual(get_release_subdir("Hitlist 2026.07.31"), "Hitlists")
        self.assertEqual(get_release_subdir("Other Folder"), "")

    def test_join_target_path(self):
        # Linux remote paths
        self.assertEqual(
            join_target_path("/mnt/virt/Comics/0. Released Comics/", "0-Days"),
            "/mnt/virt/Comics/0. Released Comics/0-Days/"
        )
        self.assertEqual(
            join_target_path("/mnt/virt/Comics/0. Released Comics", "Hitlists"),
            "/mnt/virt/Comics/0. Released Comics/Hitlists/"
        )
        self.assertEqual(
            join_target_path("/mnt/virt/Comics/0. Released Comics/", ""),
            "/mnt/virt/Comics/0. Released Comics/"
        )

        # Windows paths with forward or back slashes
        self.assertEqual(
            join_target_path("Y:/0. Released Comics/", "0-Days"),
            "Y:/0. Released Comics/0-Days/"
        )
        self.assertEqual(
            join_target_path("Y:\\0. Released Comics", "Hitlists"),
            "Y:\\0. Released Comics\\Hitlists\\"
        )

    def test_is_release_folder(self):
        self.assertTrue(is_release_folder("0-Day - 2024-01-03"))
        self.assertTrue(is_release_folder("Hitlist - 2024-01-03"))
        self.assertFalse(is_release_folder("Other - 2024-01-03"))
        self.assertFalse(is_release_folder("Random File.cbr"))

    def test_is_already_downloaded_or_queued(self):
        # 1. In queue
        self.assertTrue(is_already_downloaded_or_queued("0-Day - 2024-01-01", "2024.01", self.incoming_dir, self.input_dir, {"0-Day - 2024-01-01"}))

        # 2. In incoming (existing destination folder should still return False so new files can be queued)
        month_dir = self.incoming_dir / "2024.01"
        month_dir.mkdir()
        (month_dir / "0-Day - 2024-01-02").mkdir()
        self.assertFalse(is_already_downloaded_or_queued("0-Day - 2024-01-02", "2024.01", self.incoming_dir, self.input_dir, set()))

        # 3. In input 0-Days (existing destination folder should still return False so new files can be queued)
        zero_days_dir = self.input_dir / "0-Days"
        zero_days_dir.mkdir()
        (zero_days_dir / "0-Day - 2024-01-03").mkdir()
        self.assertFalse(is_already_downloaded_or_queued("0-Day - 2024-01-03", "2024.01", self.incoming_dir, self.input_dir, set()))

        # 4. In input Hitlists (existing destination folder should still return False so new files can be queued)
        hitlists_dir = self.input_dir / "Hitlists"
        hitlists_dir.mkdir()
        (hitlists_dir / "Hitlist - 2024-01-04").mkdir()
        self.assertFalse(is_already_downloaded_or_queued("Hitlist - 2024-01-04", "2024.01", self.incoming_dir, self.input_dir, set()))

        # 5. Not downloaded anywhere
        self.assertFalse(is_already_downloaded_or_queued("0-Day - 2024-01-05", "2024.01", self.incoming_dir, self.input_dir, set()))

    @patch("Scripts.check_for_new_releases.get_queue_bundles")
    def test_check_and_download_releases_destination_folder_exists(self, mock_queue):
        mock_queue.return_value = []
        mock_session = MagicMock()
        mock_session.list_directory.side_effect = lambda path: {
            "/New Releases/": [
                {"name": "2024.01", "type": {"id": "directory"}, "path": "/New Releases/2024.01/"}
            ],
            "/New Releases/2024.01/": [
                {"name": "0-Day - 2024-01-02", "type": {"id": "directory"}, "path": "/New Releases/2024.01/0-Day - 2024-01-02/"}
            ]
        }.get(path, [])

        # Create destination folder locally
        (self.input_dir / "0-Days" / "0-Day - 2024-01-02").mkdir(parents=True)

        with patch("Scripts.check_for_new_releases.preferences.air_released_comics_directory", "/mnt/virt/Comics/0. Released Comics/"), \
             patch("Scripts.check_for_new_releases.preferences.incoming_directory", str(self.incoming_dir)), \
             patch("Scripts.check_for_new_releases.preferences.input_directory", str(self.input_dir)), \
             patch("Scripts.check_for_new_releases.preferences.air_share_path", "/New Releases/"):

            queued = check_and_download_releases(share_path="/New Releases/", session=mock_session)

            self.assertEqual(queued, ["0-Day - 2024-01-02"])
            mock_session.download_directory.assert_called_once_with(
                remote_path="/New Releases/2024.01/0-Day - 2024-01-02/",
                target_directory="/mnt/virt/Comics/0. Released Comics/0-Days/",
                target_name="0-Day - 2024-01-02"
            )

    @patch("Scripts.check_for_new_releases.get_queue_bundles")
    def test_check_and_download_releases(self, mock_queue):
        mock_queue.return_value = [{"name": "0-Day - 2024-01-01", "target": "/mnt/virt/Comics/0. Released Comics/0-Days/0-Day - 2024-01-01"}]

        mock_session = MagicMock()
        mock_session.list_directory.side_effect = lambda path: {
            "/New Releases/": [
                {"name": "2024.01", "type": {"id": "directory"}, "path": "/New Releases/2024.01/"},
                {"name": "readme.txt", "type": {"id": "file"}, "path": "/New Releases/readme.txt"}
            ],
            "/New Releases/2024.01/": [
                {"name": "0-Day - 2024-01-01", "type": {"id": "directory"}, "path": "/New Releases/2024.01/0-Day - 2024-01-01/"},
                {"name": "0-Day - 2024-01-02", "type": {"id": "directory"}, "path": "/New Releases/2024.01/0-Day - 2024-01-02/"},
                {"name": "Hitlist - 2024-01-02", "type": {"id": "directory"}, "path": "/New Releases/2024.01/Hitlist - 2024-01-02/"},
                {"name": "unrelated_folder", "type": {"id": "directory"}, "path": "/New Releases/2024.01/unrelated_folder/"}
            ]
        }.get(path, [])

        with patch("Scripts.check_for_new_releases.preferences.air_released_comics_directory", "/mnt/virt/Comics/0. Released Comics/"), \
             patch("Scripts.check_for_new_releases.preferences.incoming_directory", str(self.incoming_dir)), \
             patch("Scripts.check_for_new_releases.preferences.input_directory", str(self.input_dir)), \
             patch("Scripts.check_for_new_releases.preferences.air_share_path", "/New Releases/"):

            queued = check_and_download_releases(share_path="/New Releases/", session=mock_session)

            self.assertEqual(queued, ["0-Day - 2024-01-02", "Hitlist - 2024-01-02"])
            self.assertEqual(mock_session.download_directory.call_count, 2)
            mock_session.download_directory.assert_any_call(
                remote_path="/New Releases/2024.01/0-Day - 2024-01-02/",
                target_directory="/mnt/virt/Comics/0. Released Comics/0-Days/",
                target_name="0-Day - 2024-01-02"
            )
            mock_session.download_directory.assert_any_call(
                remote_path="/New Releases/2024.01/Hitlist - 2024-01-02/",
                target_directory="/mnt/virt/Comics/0. Released Comics/Hitlists/",
                target_name="Hitlist - 2024-01-02"
            )

    @patch("Scripts.check_for_new_releases.get_queue_bundles")
    def test_check_and_download_releases_custom_released_directory(self, mock_queue):
        mock_queue.return_value = []
        mock_session = MagicMock()
        mock_session.list_directory.side_effect = lambda path: {
            "/NewScans/": [{"name": "2026.09", "type": {"id": "directory"}, "path": "/NewScans/2026.09/"}],
            "/NewScans/2026.09/": [
                {"name": "Hitlist 2026.07.31", "type": {"id": "directory"}, "path": "/NewScans/2026.09/Hitlist 2026.07.31/"}
            ]
        }.get(path, [])

        with patch("Scripts.check_for_new_releases.preferences.air_released_comics_directory", None), \
             patch("Scripts.check_for_new_releases.preferences.input_directory", str(self.input_dir)):

            queued = check_and_download_releases(
                target_folder="NewScans",
                released_directory="Z:/Comics/0. Released Comics/",
                session=mock_session
            )

            self.assertEqual(queued, ["Hitlist 2026.07.31"])
            mock_session.download_directory.assert_called_once_with(
                remote_path="/NewScans/2026.09/Hitlist 2026.07.31/",
                target_directory="Z:/Comics/0. Released Comics/Hitlists/",
                target_name="Hitlist 2026.07.31"
            )

    def test_find_month_directories_nested_new_releases(self):
        mock_session = MagicMock()
        mock_session.list_directory.side_effect = lambda path: {
            "/": [
                {"name": "New Releases", "type": {"id": "directory"}, "path": "/New Releases/"},
                {"name": "Other Share", "type": {"id": "directory"}, "path": "/Other Share/"}
            ],
            "/New Releases/": [
                {"name": "2024.01", "type": {"id": "directory"}, "path": "/New Releases/2024.01/"},
                {"name": "2024.02", "type": {"id": "directory"}, "path": "/New Releases/2024.02/"}
            ]
        }.get(path, [])

        month_dirs = find_month_directories(mock_session, "/")
        self.assertEqual(len(month_dirs), 2)
        self.assertEqual(month_dirs[0]["name"], "2024.01")
        self.assertEqual(month_dirs[1]["name"], "2024.02")

    def test_find_month_directories_nested_newscans(self):
        mock_session = MagicMock()
        mock_session.list_directory.side_effect = lambda path: {
            "/": [
                {"name": "NewScans", "type": {"id": "directory"}, "path": "/NewScans/"},
                {"name": "Older newscans", "type": {"id": "directory"}, "path": "/Older newscans/"}
            ],
            "/NewScans/": [
                {"name": "2026.08", "type": {"id": "directory"}, "path": "/NewScans/2026.08/"},
                {"name": "2026.09", "type": {"id": "directory"}, "path": "/NewScans/2026.09/"}
            ]
        }.get(path, [])

        month_dirs = find_month_directories(mock_session, "/New Releases/")
        self.assertEqual(len(month_dirs), 2)
        self.assertEqual(month_dirs[0]["name"], "2026.08")
        self.assertEqual(month_dirs[1]["name"], "2026.09")

    @patch("Scripts.check_for_new_releases.AirDCFilelistSession")
    @patch("Scripts.check_for_new_releases.get_queue_bundles")
    def test_check_and_download_releases_with_hub_and_target_user(self, mock_queue, mock_session_cls):
        mock_queue.return_value = []
        mock_sess = MagicMock()
        mock_sess.list_directory.side_effect = lambda path: {
            "/NewScans/": [
                {"name": "2026.09", "type": {"id": "directory"}, "path": "/NewScans/2026.09/"}
            ],
            "/NewScans/2026.09/": [
                {"name": "0-Day - 2026-09-02", "type": {"id": "directory"}, "path": "/NewScans/2026.09/0-Day - 2026-09-02/"}
            ]
        }.get(path, [])
        mock_session_cls.return_value.__enter__.return_value = mock_sess

        with patch("Scripts.check_for_new_releases.preferences.air_released_comics_directory", "/mnt/virt/Comics/0. Released Comics/"), \
             patch("Scripts.check_for_new_releases.preferences.incoming_directory", str(self.incoming_dir)), \
             patch("Scripts.check_for_new_releases.preferences.air_hub", "The Comic Shack"), \
             patch("Scripts.check_for_new_releases.preferences.air_target_user", "KT8Bot2022"), \
             patch("Scripts.check_for_new_releases.preferences.air_target_folder", "NewScans"):

            queued = check_and_download_releases()

            self.assertEqual(queued, ["0-Day - 2026-09-02"])
            mock_session_cls.assert_called_with(
                user={"nicks": "KT8Bot2022"},
                hub="The Comic Shack",
                share_profile=None,
                verbose=False
            )
            mock_sess.download_directory.assert_called_once_with(
                remote_path="/NewScans/2026.09/0-Day - 2026-09-02/",
                target_directory="/mnt/virt/Comics/0. Released Comics/0-Days/",
                target_name="0-Day - 2026-09-02"
            )

    @patch("interface_with_airdc.request_to_air")
    def test_find_user_in_hub(self, mock_req):
        def req_side_effect(endpoint, **kwargs):
            mock_resp = MagicMock()
            if endpoint == "hubs":
                mock_resp.status_code = 200
                mock_resp.json.return_value = [{"id": 1, "identity": {"name": "The Comic Shack", "connect_address": "adcs://hub.comicshack:411"}}]
            elif endpoint == "hubs/1/users/0/10000":
                mock_resp.status_code = 200
                mock_resp.json.return_value = [{"cid": "USERCID12345", "nick": "KT8Bot2022"}]
            elif endpoint == "filelists":
                mock_resp.status_code = 200
                mock_resp.json.return_value = []
            else:
                mock_resp.status_code = 404
            return mock_resp

        mock_req.side_effect = req_side_effect
        from interface_with_airdc import find_user
        user_info = find_user("KT8Bot2022", hub_identifier="The Comic Shack")
        self.assertIsNotNone(user_info)
        self.assertEqual(user_info.get("cid"), "USERCID12345")
        self.assertEqual(user_info.get("hub_url"), "adcs://hub.comicshack:411")

    @patch("interface_with_airdc.get_filelists")
    @patch("interface_with_airdc.request_to_air")
    def test_create_filelist_session_payload_fallback(self, mock_req, mock_get_filelists):
        mock_get_filelists.return_value = []
        call_count = [0]

        def req_side_effect(endpoint, **kwargs):
            mock_resp = MagicMock()
            if endpoint == "filelists" and kwargs.get("method") == "POST":
                call_count[0] += 1
                if call_count[0] == 1:
                    mock_resp.status_code = 422
                    mock_resp.json.return_value = {"message": "Invalid user schema"}
                    mock_resp.raise_for_status.side_effect = Exception("422 Client Error")
                else:
                    mock_resp.status_code = 200
                    mock_resp.json.return_value = {"id": 99, "state": {"id": "loaded"}}
                    mock_resp.raise_for_status.return_value = None
            elif endpoint == "hubs":
                mock_resp.status_code = 200
                mock_resp.json.return_value = []
            else:
                mock_resp.status_code = 200
                mock_resp.json.return_value = {"id": 99, "state": {"id": "loaded"}}
            return mock_resp

        mock_req.side_effect = req_side_effect
        session_id = create_filelist_session(user="Alice", verbose=True)
        self.assertEqual(session_id, 99)
        self.assertGreaterEqual(call_count[0], 2)

    def test_find_month_directories_verbose(self):
        mock_session = MagicMock()
        mock_session.list_directory.side_effect = lambda path: {
            "/NewScans/": [
                {"name": "2026.09", "type": {"id": "directory"}, "path": "/NewScans/2026.09/"}
            ]
        }.get(path, [])
        month_dirs = find_month_directories(mock_session, "NewScans", verbose=True)
        self.assertEqual(len(month_dirs), 1)
        self.assertEqual(month_dirs[0]["name"], "2026.09")


if __name__ == "__main__":
    unittest.main()
