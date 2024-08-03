# UltrastarParser

Contains methods to read or edit ultrastar files or directories.

## Installation

Use the package manager of your choice: [pypi](https://pypi.org/project/ultrastarParser/).

## Usage tips

- Make a backup of the text files. The library currently does not touch any other files. Though I try very hard to fix bugs and use the library myself, I cannot guarantee your files won't go up in flames, particularly if you are using a non-standard file structure or encoding. If something does go wrong, please file an issue.
- Methods will delete information. For example, comments interlaced with the attributes will not be saved and subsequently overwritten when writing. Changing the version of a song doesn't technically remove information, but could result in your program not being able to parse the file. Programs should disclose what version of the [ultrastar file format](https://usdx.eu/format) they are compatible with, but this might not be correct.
- Ultrastar librarys should be structured like below. Not following this will probably still work, but is not recommended and could cause issues in the future.

```ascii
library_folder/
├── song_1/
│   ├── song_1.txt
│   ├── song_1.mp3
│   └── ...
├── song_2/
│   ├── song_2.txt
│   ├── song_2.m4a
│   ├── song_2 [CO].jpg
│   └── ...
└── song_3/
    └── ...
```

## Features

```python
from ultrastarparser import Song, Library


song = Song('path_to_txt_file')
song.get_attribute('ARTIST') # Returns song artist
song.set_attribute('ARTIST', 'Bon Jovi') # Set song artist
song.set_version('1.1.0') # Set song file version. See https://usdx.eu/format.
song.flush() # Flush changes made to the file system. 


lib = Library('path_to_library')
for s in lib:
    # check for somthing in every song
songs_by_bon_jovi = lib.search('ARTIST', 'Bon Jovi') # Returns all songs with Bon Jovi as artist
lib.export('export_path', 'json') # exports library to path as certain format. 
```

## Planned features

- Many more docstrings
- Ability to backup files, for example before overwriting
- Logging
- Better error handling (and documentation of error handling)
- Metadata extraction not from txt file (e.g. song duration from audio file or video resolution from video file)

## Unplanned features

- Editing the songtext and notes
