"""
Unit tests for the Auto-Update System.
"""
import unittest
from unittest.mock import patch, MagicMock
import json
import io

from systems.updater import (
    parse_version,
    is_newer_version,
    select_best_asset,
    UpdateManager,
    UpdateState,
    UpdateInfo,
)


class TestUpdaterVersionComparison(unittest.TestCase):
    def test_parse_version(self):
        self.assertEqual(parse_version("1.2"), (1, 2, 0))
        self.assertEqual(parse_version("v1.2"), (1, 2, 0))
        self.assertEqual(parse_version("V1.2.0"), (1, 2, 0))
        self.assertEqual(parse_version("1.2.1"), (1, 2, 1))
        self.assertEqual(parse_version("2.0.0"), (2, 0, 0))
        self.assertEqual(parse_version("v1.3-beta"), (1, 3, 0))
        self.assertEqual(parse_version(""), (0, 0, 0))

    def test_is_newer_version(self):
        self.assertTrue(is_newer_version("v1.3.0", "1.2.0"))
        self.assertTrue(is_newer_version("1.2.1", "1.2.0"))
        self.assertTrue(is_newer_version("v2.0", "1.2.0"))
        self.assertFalse(is_newer_version("v1.2", "1.2.0"))
        self.assertFalse(is_newer_version("1.2.0", "1.2.0"))
        self.assertFalse(is_newer_version("1.1.0", "1.2.0"))
        self.assertFalse(is_newer_version("1.0.5", "1.2.0"))


class TestAssetSelection(unittest.TestCase):
    def test_select_best_asset_prefers_setup_exe(self):
        assets = [
            {"name": "CryptOfTheNecrolord_v1.2.0_win64.zip", "browser_download_url": "http://example.com/zip"},
            {"name": "CryptOfTheNecrolord_Setup_v1.2.0.exe", "browser_download_url": "http://example.com/setup"},
            {"name": "other_file.txt", "browser_download_url": "http://example.com/txt"}
        ]
        best = select_best_asset(assets)
        self.assertIsNotNone(best)
        self.assertEqual(best["name"], "CryptOfTheNecrolord_Setup_v1.2.0.exe")

    def test_select_best_asset_fallback_any_exe(self):
        assets = [
            {"name": "CryptOfTheNecrolord_v1.2.0_win64.zip", "browser_download_url": "http://example.com/zip"},
            {"name": "GameRunner.exe", "browser_download_url": "http://example.com/exe"},
        ]
        best = select_best_asset(assets)
        self.assertIsNotNone(best)
        self.assertEqual(best["name"], "GameRunner.exe")

    def test_select_best_asset_fallback_zip(self):
        assets = [
            {"name": "notes.md", "browser_download_url": "http://example.com/md"},
            {"name": "CryptOfTheNecrolord_v1.2.0_win64.zip", "browser_download_url": "http://example.com/zip"},
        ]
        best = select_best_asset(assets)
        self.assertIsNotNone(best)
        self.assertEqual(best["name"], "CryptOfTheNecrolord_v1.2.0_win64.zip")

    def test_select_best_asset_empty(self):
        self.assertIsNone(select_best_asset([]))


class TestUpdateManager(unittest.TestCase):
    @patch("urllib.request.urlopen")
    def test_check_for_updates_found_newer(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "tag_name": "v1.3.0",
            "name": "Crypt of the Necrolord v1.3",
            "body": "Exciting new features!",
            "html_url": "https://github.com/isaiah-sudo/rougelike/releases/tag/v1.3.0",
            "assets": [
                {
                    "name": "CryptOfTheNecrolord_Setup_v1.3.0.exe",
                    "browser_download_url": "https://github.com/download/Setup.exe",
                    "size": 25000000
                }
            ]
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        mgr = UpdateManager(current_version="1.2.0")
        mgr.check_for_updates(async_check=False)

        self.assertEqual(mgr.state, UpdateState.UPDATE_AVAILABLE)
        self.assertIsNotNone(mgr.update_info)
        self.assertEqual(mgr.update_info.version_str, "1.3.0")
        self.assertEqual(mgr.update_info.asset_name, "CryptOfTheNecrolord_Setup_v1.3.0.exe")

    @patch("urllib.request.urlopen")
    def test_check_for_updates_up_to_date(self, mock_urlopen):
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({
            "tag_name": "v1.2.0",
            "name": "Crypt of the Necrolord v1.2",
            "body": "Already up to date",
            "assets": []
        }).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        mgr = UpdateManager(current_version="1.2.0")
        mgr.check_for_updates(async_check=False)

        self.assertEqual(mgr.state, UpdateState.UP_TO_DATE)
        self.assertIsNone(mgr.update_info)

    @patch("urllib.request.urlopen")
    def test_check_for_updates_network_error(self, mock_urlopen):
        mock_urlopen.side_effect = Exception("Connection timed out")

        mgr = UpdateManager(current_version="1.2.0")
        mgr.check_for_updates(async_check=False)

        self.assertEqual(mgr.state, UpdateState.ERROR)
        self.assertIn("Connection timed out", mgr.error_message)

    @patch("urllib.request.urlopen")
    def test_download_update(self, mock_urlopen):
        mgr = UpdateManager(current_version="1.2.0")
        mgr.update_info = UpdateInfo(
            tag_name="v1.3.0",
            title="Crypt of the Necrolord v1.3",
            body="Notes",
            html_url="https://github.com/isaiah-sudo/rougelike",
            asset_name="Test_Setup.exe",
            asset_url="https://github.com/download/Test_Setup.exe",
            asset_size=100
        )
        fake_data = b"X" * 100
        mock_resp = MagicMock()
        mock_resp.headers = {"Content-Length": "100"}
        mock_resp.read.side_effect = [fake_data, b""]
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp

        mgr.start_download(async_download=False)
        self.assertEqual(mgr.state, UpdateState.DOWNLOADED)
        self.assertEqual(mgr.progress, 1.0)
        self.assertIsNotNone(mgr.downloaded_path)

    @patch("subprocess.Popen")
    def test_apply_update(self, mock_popen):
        import tempfile, os
        mgr = UpdateManager(current_version="1.2.0")
        with tempfile.NamedTemporaryFile(suffix=".exe", delete=False) as f:
            temp_path = f.name
        try:
            mgr.downloaded_path = temp_path
            res = mgr.apply_update()
            self.assertTrue(res)
            self.assertEqual(mgr.state, UpdateState.APPLYING)
            mock_popen.assert_called_once()
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)


class TestTitleViewUpdaterIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import pygame
        pygame.init()
        pygame.font.init()

    @patch("systems.updater.UpdateManager.check_for_updates")
    def test_title_view_update_available_flow(self, mock_check):
        import pygame
        from views.title_view import TitleView

        view = TitleView()
        view.updater.state = UpdateState.UPDATE_AVAILABLE
        view.updater.update_info = UpdateInfo(
            tag_name="v1.3.0",
            title="Crypt of the Necrolord v1.3",
            body="New content: bosses, cards",
            html_url="https://github.com/isaiah-sudo/rougelike",
            asset_name="CryptOfTheNecrolord_Setup_v1.3.0.exe",
            asset_url="https://github.com/download/Setup.exe",
            asset_size=20000000
        )

        # Test clicking NOTES button
        notes_pos = view.notes_btn.rect.center
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': notes_pos})
        action, _ = view.handle_event(click_event, notes_pos)
        self.assertEqual(action, "none")
        self.assertTrue(view.showing_notes)

        # Test closing notes
        close_pos = view.modal_close_btn.rect.center
        close_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': close_pos})
        action, _ = view.handle_event(close_event, close_pos)
        self.assertFalse(view.showing_notes)

        # Test clicking DOWNLOAD & APPLY button
        with patch.object(view.updater, "start_download") as mock_download:
            apply_pos = view.apply_btn.rect.center
            apply_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': apply_pos})
            action, _ = view.handle_event(apply_event, apply_pos)
            mock_download.assert_called_once()

    @patch("systems.updater.UpdateManager.check_for_updates")
    def test_title_view_restart_and_apply(self, mock_check):
        import pygame
        from views.title_view import TitleView

        view = TitleView()
        view.updater.state = UpdateState.DOWNLOADED
        view.updater.update_info = UpdateInfo(
            tag_name="v1.3.0",
            title="Crypt of the Necrolord v1.3",
            body="Notes",
            html_url="https://github.com/isaiah-sudo/rougelike",
            asset_name="CryptOfTheNecrolord_Setup_v1.3.0.exe",
            asset_url="https://github.com/download/Setup.exe",
            asset_size=20000000
        )

        with patch.object(view.updater, "apply_update", return_value=True) as mock_apply:
            restart_pos = view.restart_btn.rect.center
            click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': restart_pos})
            action, data = view.handle_event(click_event, restart_pos)
            mock_apply.assert_called_once()
            self.assertEqual(action, "quit_for_update")

    @patch("systems.updater.UpdateManager.check_for_updates")
    def test_title_view_draw_all_states(self, mock_check):
        import pygame
        from views.title_view import TitleView

        surface = pygame.Surface((1280, 720))
        view = TitleView()

        # Draw CHECKING
        view.updater.state = UpdateState.CHECKING
        view.draw(surface)

        # Draw UP_TO_DATE
        view.updater.state = UpdateState.UP_TO_DATE
        view.draw(surface)

        # Draw ERROR
        view.updater.state = UpdateState.ERROR
        view.updater.error_message = "Network timeout"
        view.draw(surface)

        # Draw UPDATE_AVAILABLE
        view.updater.state = UpdateState.UPDATE_AVAILABLE
        view.updater.update_info = UpdateInfo(
            tag_name="v1.3.0",
            title="Crypt of the Necrolord v1.3",
            body="### Changes\n- Boss nerfs\n- New cards",
            html_url="https://github.com/isaiah-sudo/rougelike",
            asset_name="CryptOfTheNecrolord_Setup_v1.3.0.exe",
            asset_url="https://github.com/download/Setup.exe",
            asset_size=20000000
        )
        view.draw(surface)

        # Draw DOWNLOADING
        view.updater.state = UpdateState.DOWNLOADING
        view.updater.progress = 0.45
        view.updater.bytes_downloaded = 9000000
        view.updater.total_bytes = 20000000
        view.draw(surface)

        # Draw DOWNLOADED
        view.updater.state = UpdateState.DOWNLOADED
        view.draw(surface)

        # Draw with notes modal open
        view.showing_notes = True
        view.draw(surface)


if __name__ == "__main__":
    unittest.main()
