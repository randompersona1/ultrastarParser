import ultrastarparser.io as io
import ultrastarparser.versions as versions
import os


class Song:
    """
    Represents an Ultrastar song.
    """

    def __init__(self, txt_file_path: str) -> None:
        """
        :param txt_file_path: Path to the Ultrastar song file. The folder
        containing the song file is considered the song folder and should not
        contain any more ultrastar text files.
        """
        self.reader_writer = io.UltrastarReaderWriter(txt_file_path)
        self.parse()

        self.songfolder = os.path.dirname(txt_file_path)
        self.common_name = (
            f"{self.get_attribute("ARTIST")} - {self.get_attribute("TITLE")}"
        )

    def parse(self) -> None:
        """
        Parse the song file. This is done automatically when the song is created.
        Reparsing the song before flushing changes resets the changes made to the
        song.
        """
        self.reader_writer.read()

    def get_attribute(self, attribute: str) -> str | None:
        """
        Get an attribute from the song.

        :param attribute: The attribute to get.
        """
        return self.reader_writer.song.get_attribute(attribute.upper())

    def get_attributes(self) -> dict[str, str]:
        """
        Get all attributes from the song.

        :return: A dictionary of all attributes in the song.
        """
        return self.reader_writer.song.get_attributes()

    def set_attribute(self, attribute: str, value: str) -> None:
        """
        Set an attribute in the song.

        :param attribute: The attribute to set.
        :param value: The value to set the attribute to.
        """
        self.reader_writer.song._attributes[attribute.upper()] = value

    def get_songtext(self) -> str:
        """
        Get the song text of the song.

        :return: The song text.
        """
        return self.reader_writer.song.get_body()

    def get_version(self) -> str:
        """
        Get the version of the ultrastar song file.

        :return: The version of the ultrastar song file.
        """
        return str(self.reader_writer.song.get_version())

    def set_version(self, dest_version: str) -> None:
        """
        Set the version of the ultrastar song file. Upgrades or downgrades the
        song to the desired version. This may result in data loss if the version
        to be changed to or an intermediate version removes attributes or changes
        the format of the song.

        This operation is not reversible. Upgrading a song to a higher version and
        then downgrading it to the original version might not result in the same
        song as the original.

        Some attributes' values will be lost. For example, version 1.0.0 depreciates
        the "DUETSINGERPX" attributes. However, we cannot naively copy these values
        to the new "PX" attributes, as those also existed before version 1.0.0. In this
        case, the values are lost.

        :param dest_version: The version to change the song to.
        """
        dest_version = versions.FormatVersion(dest_version)
        current_version = versions.FormatVersion(self.get_version())
        if dest_version == current_version:
            return
        available_versions = versions.versions
        if dest_version not in available_versions.keys():
            raise ValueError(
                f"This version doesn't exist or is unsupported: {dest_version}"
            )
        upgrade = dest_version > current_version

        # Upgrade or downgrade version until it matches the desired version
        while current_version != dest_version:
            if upgrade:
                try:
                    self.reader_writer.song = self.reader_writer.song.upgrade()
                except versions.VersionChangeError:
                    return
            else:
                try:
                    self.reader_writer.song = self.reader_writer.song.downgrade()
                except versions.VersionChangeError:
                    return

    def get_primary_audio(self) -> str | None:
        """
        Get the primary audio file of the song.

        :return: The primary audio file of the song.
        """
        return self.reader_writer.song.get_primary_audio()

    def flush(self) -> None:
        """
        Flush changes to the song file to the file system. Until this method is
        called, changes are only stored in memory.
        """
        self.reader_writer.write()

    def backup(self, backup_folder: str) -> None:
        """
        Backup the song file to a folder.

        :param backup_folder: The folder to backup the song to.
        """
        raise NotImplementedError("This method is not implemented yet.")

    def __str__(self) -> str:
        return self.common_name

    def __repr__(self) -> str:
        return f"Song: {self.common_name}"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Song):
            return False
        return self.reader_writer == other.reader_writer

    def __hash__(self) -> int:
        return hash(self.reader_writer)
