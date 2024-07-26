import os
import requests
from enum import Enum
from tinytag import TinyTag
from ultrastarParser.usdx_format import (
    USDX_ALL,
    USDX_FILES,
    USDX_NUMBERS,
    USDX_REQUIRED,
    USDX_URLS
)


class ReturnCode(Enum):
    OK = 0
    MISSING = 1
    ERROR = 2


class UltrastarFile:
    '''
    Represents an UltraStar song file that conforms to https://usdx.eu/format.
    If the format differs, a best effort is made. Be aware that formats other
    than utf-8 without BOM could cause issues.
    '''
    # UltraStar format version the parser is primarily compatible with. Refer
    # to https://usdx.eu/format for more information.
    _VERSION: str = 'v1.1.0'

    def __init__(self, path: str, file_encoding: str = 'utf-8') -> None:
        '''
        :param path: The path to the UltraStar file.
        :param file_encoding: The encoding of the file. Default is 'utf-8'.
        Other file encodings will probaby cause issues.
        '''

        self.path = path
        self.file_encoding = file_encoding

        self.attributes: dict[str, str]
        self.songtext: list[str]

        self.commonname: str = os.path.splitext(os.path.basename(path))[0]
        self.songfolder = os.path.dirname(path)

        self.parse()

    def parse(self) -> None:
        '''
        Reparses the file to update the attributes. This is called
        automatically when the class is initialized. Attributes are
        converted to uppercase to make them case-insensitive.
        If a version tag is not yet present, it will be added automatically.
        '''
        self.attributes = {}
        self.songtext = []
        with open(self.path, 'r', encoding=self.file_encoding) as file:
            reading_attributes = True
            lines = file.readlines()
            for line in lines:
                # Remove BOM character if present
                if (line.startswith('\ufeff') and
                        self.file_encoding == 'utf-8'):
                    line = line.lstrip('\ufeff')
                if line.startswith('#') and reading_attributes:
                    attribute = line.split(':')[0].upper()
                    value = line.split(':')[1].strip()
                    if attribute in self.attributes:
                        print(f'Warning: Duplicate attribute {attribute}'
                              f'in {self.path}. Not adding {value}.')
                        continue
                    if value == '':
                        value = None
                    self.attributes[attribute] = value
                elif line == '\n' and reading_attributes:
                    continue
                else:
                    reading_attributes = False
                    self.songtext.append(line)

        if not self.attribute_exists('#VERSION'):
            self.set_attribute('#VERSION', self._VERSION)

    def get_attribute(self, attribute: str) -> str:
        '''
        Returns the value of the attribute (e.g., '#ARTIST' -> 'Artist Name').
        If not present, returns None.
        '''
        return self.attributes.get(attribute.upper(), None)

    def set_attribute(self, attribute: str, value: str) -> None:
        '''
        Sets the value of the attribute. There is no need to reparse the file
        after setting an attribute. If the attribute is not already present,
        it will be added at the end since we cannot know where it should be
        placed if the other attributes are not in order.

        :param attribute: The attribute to set (e.g., '#ARTIST').
        :param value: The value of the attribute (e.g., 'Bon Jovi').
        '''
        self.attributes[attribute.upper()] = value

    def attribute_exists(self, attribute: str) -> bool:
        '''
        Checks whether the attribute exists in the UltraStar file.

        :param attribute: The attribute to check.
        :return: True if the attribute exists, False otherwise.
        '''
        return attribute.upper() in self.attributes.keys()

    def check(self, required: list[str] = None,
              ) -> tuple[ReturnCode, list[str], list[str]]:
        '''
        Checks whether all required attributes are present according to
        https://usdx.eu/format. If you need custom required attributes,
        you can provide a list of them like ['#TITLE', '#ARTIST', '#MP3', ...].

        Returns a specific tuple:
        - The first element is the status of the file. It is ReturnCode.OK if
        all required attributes are present, ReturnCode.MISSING if some are
        missing, and ReturnCode.ERROR if there are extra attributes.
        - The second element is a list of missing required attributes.
        - The third element is a list of extra attributes.

        :param required: A list of required attributes like ['#TITLE',
        '#ARTIST', ...]. If not provided, the default list is used.
        :return: A tuple with the status, missing required attributes, and
        extra attributes.
        '''
        # Required attributes according to https://usdx.eu/format/
        required_attributes = USDX_REQUIRED
        if required is not None:
            required_attributes = required

        missing_required = [attr for attr in required_attributes
                            if attr not in self.attributes]
        extra_attributes = [attr for attr, value in self.attributes.items()
                            if value is None]

        if len(missing_required) == 0 and len(extra_attributes) == 0:
            returncode = ReturnCode.OK
        elif len(missing_required) > 0:
            returncode = ReturnCode.MISSING
        else:
            returncode = ReturnCode.ERROR

        return returncode, missing_required, extra_attributes

    def reorder_auto(self, order: list[str] = None) -> None:
        '''
        Automatically reorders attributes according to https://usdx.eu/format/.
        It's also possible to provide a custom order.

        :param order: A custom order of attributes like ['#TITLE', '#ARTIST',
        '#MP3', ...]. If not provided, the default order is used.
        '''
        # Perfect order according to https://usdx.eu/format/
        usdx_order = USDX_ALL
        if order is not None:
            usdx_order = order

        file_line: int = 0
        for attr in usdx_order:
            if attr in self.attributes:
                self.reorder_attribute(
                    list(self.attributes.keys()).index(attr),
                    file_line
                )
                file_line += 1

    def validate_attributes(self,
                            attributes_with_paths: list[str] | None = None,
                            attributes_numbers: list[str] | None = None,
                            attributes_urls: list[str] | None = None
                            ) -> list[str]:
        '''
        Validates the file by checking attributes. Checks that files exist and
        that numbers are valid.

        :param attributes_with_paths: A list of attributes that refer to files
        like '#MP3', '#AUDIO', '#COVER', '#BACKGROUND', '#VIDEO', etc. If not
        provided, the default list is used.
        :param attributes_numbers: A list of attributes that refer to numbers
        like '#BPM', '#GAP', etc. If not provided, the default list is used.
        :return: A list of attributes that are faulty.
        '''
        if attributes_with_paths is None:
            attributes_with_paths = USDX_FILES

        if attributes_numbers is None:
            attributes_numbers = USDX_NUMBERS

        if attributes_urls is None:
            attributes_urls = USDX_URLS

        faulty_attributes = []

        for attr in attributes_with_paths:
            if attr in self.attributes:
                if not os.path.exists(os.path.join(self.songfolder,
                                                   self.get_attribute(attr))):
                    faulty_attributes.append(attr)

        for attr in attributes_numbers:
            if attr in self.attributes:
                try:
                    value = float(self.get_attribute(attr))
                    if value < 0:
                        raise ValueError
                except ValueError:
                    faulty_attributes.append(attr)

        for attr in attributes_urls:
            if attr in self.attributes:
                if not self.get_attribute(attr).startswith('http'):
                    faulty_attributes.append(attr)

        return faulty_attributes

    def validate_karaoke(self) -> ReturnCode:
        '''
        Validates that the karaoke files (#VOCALS and #INSTRUMENTAL) are
        present and have the same duration as the audio file.

        :return: ReturnCode.OK if the karaoke files are valid,
        ReturnCode.MISSING if some files are missing, ReturnCode.Error
        if the files have differend durations.
        '''
        audio = self.audio_path()
        vocals = self.get_attribute('#VOCALS')
        instrumental = self.get_attribute('#INSTRUMENTAL')

        if audio is None or vocals is None or instrumental is None:
            return ReturnCode.MISSING
        if not os.path.exists(os.path.join(self.songfolder, audio)):
            return ReturnCode.MISSING
        if not os.path.exists(os.path.join(self.songfolder, vocals)):
            return ReturnCode.MISSING
        if not os.path.exists(os.path.join(self.songfolder, instrumental)):
            return ReturnCode.MISSING

        audio_duration = self.audio_duration()
        vocals_duration = TinyTag.get(
            os.path.join(self.songfolder, vocals)).duration
        instrumental_duration = TinyTag.get(
            os.path.join(self.songfolder, instrumental)).duration
        if not (audio_duration == vocals_duration == instrumental_duration):
            return ReturnCode.ERROR

        return ReturnCode.OK

    def is_duet(self) -> bool:
        '''
        Checks if the song is a duet by searching for different things. Just
        because a song is a duet does not mean that it works in UltraStar.

        :return: True if the song is a duet, False otherwise.
        '''
        # Check for P1 and P2 attributes
        if (self.get_attribute('#P1') is not None or
                self.get_attribute('#P2') is not None):
            return True

        # Check for 'P1' or 'P2' in the songtext
        for line in self.songtext:
            if 'p1' in line.lower() or 'p2' in line.lower():
                return True

        # Check for '[DUET]-Songs' as edition
        if self.get_attribute('#EDITION') == '[DUET]-Songs':
            return True

        return False

    def validate_duet(self) -> int:
        '''
        Validates that a duet has all necessary features.

        :return:
        0 if the song is fully valid
        1 if the song is a duet with incorrect attributes
        2 if the song is a duet but missing P1 or P2 markers in the songtext
        3 if the song is not a duet
        '''

        if not self.is_duet():
            return 3

        # Check P1 and P2 attributes
        if (self.get_attribute('P1') is None or
                self.get_attribute('P2') is None):
            return 1

        # Check for 'P1' and 'P2' in the songtext
        p1exists = False
        p2exists = False
        for line in self.songtext:
            if 'p1' in line.lower():
                p1exists = True
                if p2exists:
                    break
            if 'p2' in line.lower():
                p2exists = True
                if p1exists:
                    break
        if not p1exists or not p2exists:
            return 2

        return 0

    def validate_urls(self, urls: list[str] | None = None) -> list[str]:
        '''
        Validates that the URLs are active. Checks all URLs in the file. If
        anything but a 200 status code is returned, the URL is considered
        faulty. This method can take a long time if many URLs are checked.

        Be aware that a 200 status code does not guarantee that the
        URL is correct.

        :param urls: A list of attributes that refer to URLs like '#AUDIOURL'.
        If not provided, the default list is used.
        :return: A list of attributes with faulty URLs.
        '''
        if urls is None:
            urls = USDX_URLS

        faulty_urls = []

        for attr in urls:
            if attr in self.attributes:
                try:
                    response: requests.Response
                    response = requests.get(self.get_attribute(attr))
                    if response.status_code != 200:
                        faulty_urls.append(attr)
                except requests.exceptions.RequestException:
                    faulty_urls.append(attr)
        del response
        return faulty_urls

    def reorder_attribute(self, old_index: int, new_index: int) -> None:
        '''
        Reorders the attribute at old_index to new_index.

        :param old_index: The current index of the attribute.
        :param new_index: The new index of the attribute.
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
        Removes the attribute from the UltraStar file.

        :param attribute: The attribute to remove.
        '''
        self.attributes.pop(attribute.upper())

    def audio_path(self) -> str:
        '''
        Returns the path to the MP3 file associated with the UltraStar file.
        This method exists tries to get the #MP3 attribute. If it does not
        exist, return #AUDIO.

        :return: The path to the associated audio file.
        '''
        if self.get_attribute('#MP3') is not None:
            return self.get_attribute('#MP3')
        else:
            return self.get_attribute('#AUDIO')

    def audio_duration(self) -> float | None:
        '''
        Returns the duration of the audio file in seconds. If the audio file
        does not exist, returns None.

        :return: The duration of the audio file in seconds.
        '''
        try:
            tag = TinyTag.get(os.path.join(self.songfolder, self.audio_path()))
            return tag.duration
        except FileNotFoundError:
            return None

    def audio_filesize(self) -> int | None:
        '''
        Returns the size of the audio file in bytes. If the audio file does
        not exist, returns None.

        :return: The size of the audio file in bytes.
        '''
        try:
            tag = TinyTag.get(os.path.join(self.songfolder, self.audio_path()))
            return tag.filesize
        except FileNotFoundError:
            return None

    def flush(self):
        '''
        Flush changes to the file system. This will overwrite the original
        file and is irreversible.
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
        if isinstance(other, UltrastarFile):
            return (
                self.attributes == other.attributes and
                self.songtext == other.songtext
            )
        else:
            return False
