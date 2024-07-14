import os

class UltraStarFile:
    '''
    Represents an UltraStar file. 
    '''
    def __init__(self, path: str, file_encoding: str = 'utf-8') -> None:
        self.path = path
        self.file_encoding = file_encoding
        self.attributes = {}

        self.parse()

    def parse(self) -> None:
        '''
        Reparses the file to update the attributes dictionary. This is called automatically when the class is initialized.
        '''
        with open(self.path, 'r', encoding=self.file_encoding) as file:
            lines = file.readlines()
            for line in lines:
                if line.startswith('#'):
                    self.attributes[line.split(':')[0]] = line.split(':')[1].strip()
    
    def get_attribute(self, attribute: str) -> str:
        '''
        Returns the value of the attribute (e.g., '#ARTIST' -> 'Artist Name')
        '''
        return self.attributes.get(attribute, None)

    def set_attribute(self, attribute: str, value: str) -> None:
        '''
        Sets the value of the attribute (e.g., '#ARTIST', 'Artist Name'). Currently only supports setting existing attributes. There is no need to reparse the file after setting an attribute.
        '''
        with open(self.path, 'r', encoding=self.file_encoding) as temp_file:
            lines = temp_file.readlines()
        for i in range(len(lines)):
            if lines[i].startswith(attribute):
                lines[i] = attribute + ':' + value + '\n'
                break
        else:
            raise NotImplementedError(f'Attribute {attribute} not found in file')

        with open(self.path, 'w', encoding=self.file_encoding) as file:
            file.writelines(lines)

        self.attributes[attribute] = value

    def remove_attribute(attribute: str) -> None:
        '''
        Removes the attribute from the file. Currently not implemented.
        '''
        raise NotImplementedError('This method has not been implemented yet.')
    
    def mp3_path(self) -> str:
        '''
        Returns the path to the MP3 file associated with the UltraStar file.
        '''
        return self.get_attribute('#MP3')
    
    def __str__(self) -> str:
        return self.path
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def __eq__(self, other) -> bool:
        return self.path == other.path


class Library:
    '''
    Represents a library of UltraStar files. 
    '''
    def __init__(self, path: str) -> None:
        '''
        path: The path to the library directory.
        '''
        self.path = path
        self.songs: list[UltraStarFile] = []

        for root, _, files in os.walk(path):
            for file in files:
                if file.endswith(".txt"):
                    self.songs.append(UltraStarFile(os.path.join(root, file)))
    
    def search(self, attribute: str, value: str) -> list[UltraStarFile]:
        '''
        Search for songs with the given attribute and value.
        '''
        return [song for song in self.songs if song.get_attribute(attribute) == value]
    
    def songs(self) -> list[UltraStarFile]:
        return self.songs

    def __str__(self) -> str:
        return self.path

    def __iter__(self):
        return iter(self.songs)
    
    def __next__(self):
        return next(self.songs)
    
    def __eq__(self, other) -> bool:
        return self.path == other.path