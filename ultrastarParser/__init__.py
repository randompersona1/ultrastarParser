import os

class UltraStarFile:
    '''
    Represents an UltraStar file. 
    '''
    def __init__(self, path: str, file_encoding: str = 'utf-8') -> None:
        self.path = path
        self.file_encoding = file_encoding

        self.attributes: dict[str, str] = {}
        self.songtext: list[str] = []

        self.commonname: str = os.path.splitext(os.path.basename(path))[0]
        self.songfolder = os.path.dirname(path)

        self.parse()

    def parse(self) -> None:
        '''
        Reparses the file to update the attributes dictionary. This is called automatically when
        the class is initialized.
        '''
        self.attributes = {}
        self.songtext = []
        with open(self.path, 'r', encoding=self.file_encoding) as file:
            lines = file.readlines()
            for line in lines:
                # Remove BOM character if present
                if line.startswith('\ufeff'):
                    line = line.lstrip('\ufeff')
                if line.startswith('#'):
                    attribute = line.split(':')[0].upper()
                    value = line.split(':')[1].strip()
                    if attribute in self.attributes:
                        print(f'Warning: Duplicate attribute {attribute} in {self.path}.'
                              f'Not adding {value}.')
                        continue
                    self.attributes[attribute] = value
                elif line == '\n':
                    continue
                else:
                    self.songtext.append(line)

    def get_attribute(self, attribute: str) -> str:
        '''
        Returns the value of the attribute (e.g., '#ARTIST' -> 'Artist Name')
        '''
        return self.attributes.get(attribute.upper(), None)

    def set_attribute(self, attribute: str, value: str) -> None:
        '''
        Sets the value of the attribute (e.g., '#ARTIST', 'Artist Name'). There is no need to
        reparse the file after setting an attribute. If the attribute is not already present, it
        will be added at the end since we cannot know where it should be placed if the other
        attributes are not in order.
        '''
        self.attributes[attribute.upper()] = value

    def check(self) -> tuple[str, list[list[str], list[str]]]:
        '''
        Checks whether all required attributes are present.
        Returns a specific tuple:
        - The first element is the status of the file. It can be 'OK', 'MISSING', or 'ERROR'.
        - The second element is a list of missing required attributes.
        - The third element is a list of extra attributes.
        '''
        # Required attributes according to https://usdx.eu/format/
        required_attributes = [
            '#VERSION',
            '#TITLE',
            '#ARTIST',
            '#MP3',
            '#BPM',
            '#GAP',
        ]
        missing_required = [attr for attr in required_attributes if attr not in self.attributes]
        extra_attributes = [attr for attr, value in self.attributes.items() if value is None]

        if len(missing_required) == 0 and len(extra_attributes) == 0:
            returncode = 'OK'
        elif len(missing_required) > 0:
            returncode = 'MISSING'
        else:
            returncode = 'ERROR'

        return returncode, missing_required, extra_attributes

    def reorder_auto(self) -> None:
        '''
        Automatically reorders attributes according to https://usdx.eu/format/.
        '''
        # Perfect order according to https://usdx.eu/format/
        usdx_order = [
            '#VERSION',
            '#TITLE',
            '#ARTIST',
            '#MP3',
            '#AUDIO',
            '#BPM',
            '#GAP',
            '#COVER',
            '#BACKGROUND',
            '#VIDEO',
            '#VIDEOGAP',
            '#VOCALS',
            '#INSTRUMENTAL'
            '#GENRE',
            '#TAGS',
            '#EDITION',
            '#CREATOR',
            '#LANGUAGE',
            '#YEAR',
            '#START',
            '#END',
            '#PREVIEWSTART',
            '#MEDLEYSTARTBEAT',
            '#MEDLEYENDBEAT',
            '#CALCMEDLEY',
            '#P1',
            '#P2',
            '#PROVIDEDBY',
            '#COMMENT',
        ]

        file_line: int = 0
        for attr in usdx_order:
            if attr in self.attributes:
                self.reorder_attribute(list(self.attributes.keys()).index(attr), file_line)
                file_line += 1

    def reorder_attribute(self, old_index: int, new_index: int) -> None:
        '''
        Reorders the attribute at old_index to new_index.
        '''
        if old_index == new_index:
            return
        if old_index < 0 or old_index >= len(self.attributes):
            raise ValueError('Invalid old_index.')
        if new_index < 0 or new_index >= len(self.attributes):
            raise ValueError(f'Invalid new_index {new_index} for'
                             f'{len(self.attributes)} attributes.')

        # Convert attributes to a list of tuples (key, value)
        items = list(self.attributes.items())
        # Remove the item at old_index
        item = items.pop(old_index)
        # Insert the item at new_index
        items.insert(new_index, item)
        # Convert the list of tuples back to a dictionary
        self.attributes = dict(items)

    def remove_attribute(self, attribute: str) -> None:
        '''
        Removes the attribute
        '''
        self.attributes.pop(attribute.upper())

    def mp3_path(self) -> str:
        '''
        Returns the path to the MP3 file associated with the UltraStar file. This method exists for
        ease of use, it just calls get_attribute('#MP3').
        '''
        return self.get_attribute('#MP3')

    def flush(self):
        '''
        Flush changes to the file system.
        '''
        text = []
        for attribute, value in self.attributes.items():
            text.append(f'{attribute}:{value}\n')
        for line in self.songtext:
            text.append(line)
        with open(self.path, 'w', encoding=self.file_encoding) as file:
            file.writelines(text)

    def __str__(self) -> str:
        return self.commonname

    def __repr__(self) -> str:
        return f'UltraStarFile(path="{self.path}")'

    def __eq__(self, other) -> bool:
        return self.attributes == other.attributes and self.songtext == other.songtext


class Library:
    '''
    Represents a library of UltraStar files. Assumes that all text files in the directory are
    UltraStar files.
    '''
    def __init__(self, path: str) -> None:
        '''
        path: The path to the library directory.
        '''
        self.path = path
        self.songs: list[UltraStarFile] = []

        self.parse()

    def parse(self) -> None:
        '''
        Parses the library directory to find all UltraStar files. Called automatically on
        initialization.
        '''
        self.songs.clear()
        for root, _, files in os.walk(self.path):
            for file in files:
                if file.endswith(".txt"):
                    self.songs.append(UltraStarFile(os.path.join(root, file)))

    def search(self, attribute: str, value: str) -> list[UltraStarFile]:
        '''
        Search for songs with the given attribute and value.
        '''
        return [song for song in self.songs if song.get_attribute(attribute) == value]

    def __repr__(self) -> str:
        return f'Library(path="{self.path}")'

    def __str__(self) -> str:
        return self.path

    def __iter__(self) -> UltraStarFile:
        return iter(self.songs)

    def __next__(self) -> UltraStarFile:
        return next(self.songs)

    def __eq__(self, other) -> bool:
        return self.songs == other.songs
