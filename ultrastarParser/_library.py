import os
import shutil
import json
from csv import DictWriter
from enum import Enum
from ultrastarParser._ultrastarfile import UltrastarFile
from ultrastarParser.usdx_format import USDX_ALL


class ExportFormat(Enum):
    '''
    Enum to define the export format for the library.
    '''
    JSON = "json"
    CSV = "csv"


class Library:
    '''
    Represents a library of UltraStar files. Assumes that all text files in
    the directory are UltraStar files.
    '''
    def __init__(self, path: str) -> None:
        '''
        :param: path: The path to the library directory.
        '''
        self.path = path
        self.songs: list[UltrastarFile] = []

        self.parse()

    def parse(self) -> None:
        '''
        Parses the library directory to find all UltraStar files. Called
        automatically on initialization.
        '''
        self.songs.clear()
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.endswith(".txt"):
                    self.songs.append(UltrastarFile(os.path.join(root, file)))

    def search(self, attribute: str, value: str) -> list[UltrastarFile]:
        '''
        Search for songs with the given attribute and value like '#ARTIST',
        'Bon Jovi' -> [UltraStarFile, ...]

        :param attribute: The attribute to search for.
        :param value: The value of the attribute to search for.
        :return: A list of UltraStarFile objects that match the search.
        '''
        return [song for song in self.songs
                if song.get_attribute(attribute) == value]

    def add(self, song: UltrastarFile, delete_old_files: bool = False) -> bool:
        '''
        Adds a song to the library. This will copy all song files to the
        library folder. If an error occurs, no changes are made.

        :param song: The UltraStarFile object to add.
        :param delete_old_files: If True, the old song files will be deleted
        i.e. the song will be moved instead of copied.
        :return: True if the song was added, False if the song is already in
        the library or an error occurred while adding.
        '''
        # Check if the song is already in the library
        if song in self.songs:
            return False
        # Deeper check for the same song using the commonname
        if song.commonname in [s.commonname for s in self.songs]:
            return False
        # Additional check to assert that the song path is not in the library
        if song.path.startswith(self.path):
            return False

        # Copy the song to the library
        old_song_folder_path = song.songfolder
        new_song_folder_path = os.path.join(self.path, song.commonname)

        try:
            os.makedirs(new_song_folder_path, exist_ok=False)
        except FileExistsError:
            return False

        try:
            shutil.copy(old_song_folder_path, new_song_folder_path)
        except shutil.SameFileError:
            return False

        if delete_old_files:
            try:
                shutil.rmtree(old_song_folder_path)
            except FileNotFoundError:
                pass

        # Create new song object and add it to the library
        new_song = UltrastarFile(
            os.path.join(new_song_folder_path, song.path)
        )
        self.songs.append(new_song)
        return True

    def remove(self, song: UltrastarFile) -> bool:
        '''
        Removes a song from the library. This will delete the song folder
        and all files in it.

        :param song: The UltraStarFile object to remove.
        :return: True if the song was removed, False if the song is not in
        the library or an error occurred while removing.
        '''
        if song not in self.songs:
            return False

        if not song.path.startswith(self.path):
            return False

        try:
            shutil.rmtree(song.songfolder)
        except FileNotFoundError:
            return False

        self.songs.remove(song)
        return True

    def least_common_divisor_attributes(self) -> list[str]:
        '''
        Returns all attributes in use in the entire library.

        :return: A list of all attributes used in the library sorted to match
        the USDX format.
        '''
        attributes = set()
        for song in self.songs:
            attributes.update(song.attributes.keys())
        attributes = list(attributes)

        # Sort the attributes list according to the USDX_ALL list
        sorted_attributes = []
        for usdx_attribute in USDX_ALL:
            if usdx_attribute in attributes:
                sorted_attributes.append(usdx_attribute)

        return sorted_attributes

    def export(self,
               path: str,
               export_format: ExportFormat,
               attributes: list[str] | None = None
               ) -> None:
        '''
        Exports the library to a file. Exports only necessary attributes
        by default.

        :param path: The path to the json file.
        :param export_format: The format to export the library to. Can be
        ExportFormat.JSON or ExportFormat.CSV.
        :param attributes: A list of attributes to export like ['#ARTIST',
        '#TITLE']. If not provided, all necessary attributes are exported.
        :raises ValueError: If the export format is not supported.
        :raises FileNotFoundError: If the path to the file is invalid.
        :raises PermissionError: If the file cannot be written to.
        '''
        if attributes is None:
            attributes = self.least_common_divisor_attributes()

        export_data = {}
        for song in self:
            song_data = {}
            for attribute in attributes:
                song_data[attribute] = song.get_attribute(attribute)
            export_data[song.commonname] = song_data

        match export_format:
            case ExportFormat.JSON:
                with open(file=path, mode='w') as output_file:
                    json.dump(export_data, output_file, indent=4)

            case ExportFormat.CSV:
                with open(file=path, mode='w') as output_file:
                    writer = DictWriter(f=output_file,
                                        fieldnames=attributes,
                                        dialect='excel')
                    writer.writeheader()
                    for song in export_data.values():
                        writer.writerow(song)
            case _:
                raise ValueError(f"Export format '{export_format}"
                                 f"not supported.")

    def __repr__(self) -> str:
        return f'Library(path="{self.path}")'

    def __str__(self) -> str:
        return self.path

    def __iter__(self) -> UltrastarFile:
        return iter(self.songs)

    def __next__(self) -> UltrastarFile:
        return next(self.songs)

    def __len__(self) -> int:
        return len(self.songs)

    def __getitem__(self, index: int) -> UltrastarFile:
        return self.songs[index]

    def __eq__(self, other) -> bool:
        if isinstance(other, Library):
            return self.songs == other.songs
        return False
