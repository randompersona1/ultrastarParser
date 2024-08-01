from csv import DictWriter
import os
import ultrastarparser.song as song
import json


class Library:
    def __init__(self, library_folder: str) -> None:
        self.library_folder = library_folder
        self.songs: list[song.Song] = []
        self.load_songs()

    def load_songs(self) -> None:
        self.songs.clear()
        for root, _, files in os.walk(self.library_folder):
            for file in files:
                if file.endswith(".txt"):
                    self.songs.append(song.Song(os.path.join(root, file)))

    def search(self, attribute: str, value: str) -> list[song.Song]:
        """
        Search for songs with the given attribute and value like 'ARTIST',
        'Bon Jovi' -> [UltraStarFile, ...]

        :param attribute: The attribute to search for.
        :param value: The value of the attribute to search for.
        :return: A list of UltraStarFile objects that match the search.
        """
        return [song for song in self.songs if song.get_attribute(attribute) == value]

    def least_common_divisor_attributes(self) -> list[str]:
        """
        Returns all attributes in use in the entire library.

        :return: A list of all attributes used in the library sorted to match
        the USDX format.
        """
        attributes = set()
        for ussong in self:
            attributes.update(ussong.get_attributes().keys())
        attributes = list(attributes)

        # TODO find a way to sort the attributes in a sensible way

        return attributes

    def export(
        self,
        path: str,
        export_format: str,
        attributes: list[str] | None = None,
    ) -> None:
        """
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
        """
        if attributes is None:
            attributes = self.least_common_divisor_attributes()

        export_data = {}
        for ussong in self:
            song_data = {}
            for attribute in attributes:
                song_data[attribute] = ussong.get_attribute(attribute)
            export_data[ussong.commonname] = song_data

        match export_format.upper():
            case "json":
                with open(file=path, mode="w") as output_file:
                    json.dump(export_data, output_file, indent=4)

            case "csv":
                with open(file=path, mode="w") as output_file:
                    writer = DictWriter(
                        f=output_file, fieldnames=attributes, dialect="excel"
                    )
                    writer.writeheader()
                    for ussong in export_data.values():
                        writer.writerow(ussong)
            case _:
                raise ValueError(f"Export format '{export_format}" f"not supported.")

    def get_songs(self) -> list[song.Song]:
        return self.songs

    def get_song(self, index: int) -> song.Song:
        return self.songs[index]

    def __iter__(self) -> iter:
        return iter(self.songs)

    def __next__(self) -> song.Song:
        return next(self.songs)

    def __str__(self) -> str:
        return f"Library: {self.library_folder}"

    def __repr__(self) -> str:
        return f"Library({self.library_folder})"

    def __len__(self) -> int:
        return len(self.songs)

    def __getitem__(self, index: int) -> song.Song:
        return self.get_song(index)
