import unittest
from unittest.mock import patch, mock_open
import unittest.mock

from ultrastarparser import Song, Library


test_song = "tests/4 Non Blondes - What's Up.txt"
test_song_content = """#VERSION:v1.1.0
#TITLE:What's Up?
#ARTIST:4 Non Blondes
#MP3:4 Non Blondes - What's Up.mp3
#BPM:264
#GAP:32340
#COVER:4 Non Blondes - What's Up [CO].jpg
#BACKGROUND:4 Non Blondes - What's Up [BG].jpg
#VIDEO:4 Non Blondes - What's Up.mp4
#VOCALS:4 Non Blondes - What's Up [VOC].mp3
#INSTRUMENTAL:4 Non Blondes - What's Up [INSTR].mp3
#GENRE:Alternative
#EDITION:SingStar Amped [AU]
#CREATOR:a224
#LANGUAGE:English
#YEAR:1992
#PREVIEWSTART:87.86
#MEDLEYSTART:0
#MEDLEYEND:1193"""


class TestSong(unittest.TestCase):
    def test_detect_version(self):
        song = Song(test_song)
        self.assertEqual(song.get_version(), "1.1.0")

    def test_get_attribute(self):
        song = Song(test_song)
        self.assertEqual(song.get_attribute("TITLE"), "What's Up?")

    def test_get_attribute_lower(self):
        song = Song(test_song)
        self.assertEqual(song.get_attribute("title"), "What's Up?")

    def test_upgrade(self):
        song = Song(test_song)
        song.set_version("2.0.0")
        self.assertEqual(song.get_version(), "2.0.0")
        self.assertEqual(song.get_attribute("AUDIO"), "4 Non Blondes - What's Up.mp3")

    def test_downgrade(self):
        song = Song(test_song)
        song.set_version("0.1.0")
        self.assertEqual(song.get_version(), "0.1.0")
        self.assertEqual(song.get_attribute("MP3"), "4 Non Blondes - What's Up.mp3")

    def test_get_attribute_not_found(self):
        song = Song(test_song)
        self.assertIsNone(song.get_attribute("NOTFOUND"))

    def test_equal(self):
        song1 = Song(test_song)
        song2 = Song(test_song)
        self.assertEqual(song1, song2)

    @patch("builtins.open", new_callable=mock_open, read_data=test_song_content)
    def test_flush(self, mock_file: unittest.mock.MagicMock):
        # Initial file content
        file_contents = test_song_content

        # Function to handle write operations and update the mock file content
        def write_side_effect(data):
            nonlocal file_contents
            file_contents = data

        # Mock the file read and write operations
        mock_file.return_value.read.side_effect = lambda: file_contents
        mock_file.return_value.write.side_effect = write_side_effect

        song = Song(test_song)
        song.set_attribute("TITLE", "A test title")
        song.flush()
        mock_file.assert_called_with(test_song, "w", encoding="utf-8")

        handle = mock_file()
        handle.write.assert_called()

        # Simulate reading the updated file content
        mock_file.return_value.read.side_effect = lambda: file_contents

        song.parse()
        self.assertEqual(song.get_attribute("TITLE"), "A test title")


class TestLibrary(unittest.TestCase):
    def test_search(self):
        library = Library("tests")
        songs = library.search("TITLE", "What's Up?")
        self.assertEqual(len(songs), 1)
        self.assertEqual(songs[0].get_attribute("ARTIST"), "4 Non Blondes")


if __name__ == "__main__":
    unittest.main()
