import ultrastarparser.versions as versions
import os
import shutil


class UltrastarReaderWriter:
    def __init__(self, txt_file_path) -> None:
        self.txt_file_path = txt_file_path
        self.songfolder = os.path.dirname(txt_file_path)
        self.encoding = "utf-8"

        self.song: versions.BaseUltrastarVersion

    def read(self) -> None:
        with open(
            self.txt_file_path, "r", encoding=self.encoding, errors="ignore"
        ) as f:
            lines = f.read()

        # Remove BOM if present. Fuck BOM
        lines = lines.removeprefix("\ufeff")

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

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UltrastarReaderWriter):
            return False
        return self.song == other.song
