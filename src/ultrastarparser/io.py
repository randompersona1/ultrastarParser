import ultrastarparser.versions as versions
import os
import shutil
from charamel import Detector


class UltrastarReaderWriter:
    def __init__(self, txt_file_path, detect_encoding: bool = False) -> None:
        self.txt_file_path = txt_file_path
        self.songfolder = os.path.dirname(txt_file_path)
        self.encoding = "utf-8"

        self.song: versions.BaseUltrastarVersion

    def read(self, detect_encoding: bool = False) -> None:
        with open(self.txt_file_path, "rb") as f:
            lines = f.read()
        if detect_encoding:
            detector = Detector()
            encoding = detector.detect(lines)
            lines = lines.decode(encoding=encoding)
        else:
            lines = lines.decode(encoding=self.encoding)

        self.song = versions.ultrastar_version_factory(lines)
        self.song.parse(lines)

    def write(self) -> None:
        song = ""

        for attribute in self.song.get_attributes():
            song += f"#{attribute}:{self.song._attributes[attribute]}\n"
        for line in self.song.get_body():
            song += f"{line}\n"

        with open(self.txt_file_path, "w", encoding=self.encoding) as f:
            f.write(song)

    def backup(self, backup_file_path: str, files: list[str] | None) -> None:
        """
        Backup the song to a backup folder.
        Removes existing files in the backup folder.

        :param backup_file_path: The path to the backup folder.
        :param files: Files to backup
        """
        if not os.path.exists(backup_file_path):
            os.makedirs(backup_file_path)
        elif len(os.listdir(backup_file_path)) != 0:
            os.rmdir(backup_file_path)
            os.makedirs(backup_file_path)

        if files is not None:
            shutil.copy(
                os.path.join(self.songfolder, self.txt_file_path), backup_file_path
            )
            return
        for file in files:
            shutil.copy(os.path.join(self.file), backup_file_path)
