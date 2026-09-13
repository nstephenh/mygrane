import io
import json
import unittest
from unittest.mock import MagicMock, patch

from interface_with_airdc import get_hubs, get_favorite_hubs
from Scripts.list_hubs import format_bytes, print_hubs_summary, main as list_hubs_main


class TestHubs(unittest.TestCase):

    @patch("interface_with_airdc.request_to_air")
    def test_get_hubs_list(self, mock_req):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {
                "id": 1,
                "identity": {"name": "TestHub", "connect_address": "adcs://hub.test:411"},
                "connect_state": {"id": "connected", "str": "Connected"},
                "user": {"nicks": "TestNick"},
                "counts": {"users": 100, "share_size": 1024 * 1024 * 1024}
            }
        ]
        mock_response.raise_for_status.return_value = None
        mock_req.return_value = mock_response

        hubs = get_hubs(host="http://localhost:5600")
        self.assertEqual(len(hubs), 1)
        self.assertEqual(hubs[0]["identity"]["name"], "TestHub")
        mock_req.assert_called_with("hubs", method="GET", host="http://localhost:5600", user=None, password=None)

    @patch("interface_with_airdc.request_to_air")
    def test_get_hubs_dict_response(self, mock_req):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "hubs": [
                {"id": 2, "name": "HubTwo"}
            ]
        }
        mock_response.raise_for_status.return_value = None
        mock_req.return_value = mock_response

        hubs = get_hubs()
        self.assertEqual(len(hubs), 1)
        self.assertEqual(hubs[0]["id"], 2)

    @patch("interface_with_airdc.request_to_air")
    def test_get_favorite_hubs(self, mock_req):
        mock_response = MagicMock()
        mock_response.json.return_value = [
            {"id": 1, "name": "FavHub", "hub_url": "adcs://fav.hub:411"}
        ]
        mock_response.raise_for_status.return_value = None
        mock_req.return_value = mock_response

        favs = get_favorite_hubs()
        self.assertEqual(len(favs), 1)
        self.assertEqual(favs[0]["name"], "FavHub")

    def test_format_bytes(self):
        self.assertEqual(format_bytes(0), "0 B")
        self.assertEqual(format_bytes(1024), "1.00 KB")
        self.assertEqual(format_bytes(1024 * 1024 * 500), "500.00 MB")
        self.assertEqual(format_bytes(1024 * 1024 * 1024 * 1.5), "1.50 GB")

    def test_print_hubs_summary_empty(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            print_hubs_summary([])
            self.assertIn("No active hub sessions found", mock_out.getvalue())

    def test_print_hubs_summary_populated(self):
        hubs = [
            {
                "id": 1,
                "identity": {"name": "ComicHub", "description": "Comics DC", "connect_address": "adcs://comics.dc:411"},
                "connect_state": {"id": "connected", "str": "Connected"},
                "user": {"nicks": "ComicReader"},
                "counts": {"users": 250, "share_size": 1024 * 1024 * 1024 * 1024}
            }
        ]
        with patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            print_hubs_summary(hubs)
            output = mock_out.getvalue()
            self.assertIn("ComicHub", output)
            self.assertIn("Connected", output)
            self.assertIn("adcs://comics.dc:411", output)
            self.assertIn("ComicReader", output)
            self.assertIn("1.00 TB", output)

    @patch("Scripts.list_hubs.get_hubs")
    def test_list_hubs_cli_json(self, mock_get_hubs):
        mock_get_hubs.return_value = [{"id": 1, "name": "TestHub"}]
        with patch("sys.argv", ["list_hubs.py", "--json"]), \
             patch("sys.stdout", new_callable=io.StringIO) as mock_out:
            list_hubs_main()
            output = mock_out.getvalue()
            self.assertIn('"id": 1', output)
            self.assertIn('"name": "TestHub"', output)

    @patch("Scripts.list_hubs.get_hubs")
    def test_list_hubs_cli_error(self, mock_get_hubs):
        mock_get_hubs.side_effect = ConnectionError("Connection refused")
        with patch("sys.argv", ["list_hubs.py"]), \
             patch("sys.stderr", new_callable=io.StringIO) as mock_err, \
             self.assertRaises(SystemExit) as cm:
            list_hubs_main()
        self.assertEqual(cm.exception.code, 1)
        self.assertIn("Failed to query hubs", mock_err.getvalue())


if __name__ == "__main__":
    unittest.main()
