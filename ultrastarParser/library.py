from ultrastarParser import UltraStarFile
import os

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