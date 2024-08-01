# UltrastarParser

Contains methods to read or edit ultrastar files or directories.

## Installation

Use the package manager of your choice: [pypi](https://pypi.org/project/ultrastarParser/).

## Usage tips

- Make a backup of the text files. The library currently does not touch any other files. Though I try very hard to fix bugs and use the library myself, I cannot guarantee your files won't go up in flames, particularly if you are using a non-standard file structure or encoding. If something does go wrong, please file an issue.
- Certain formattings will be lost. For example, attributes (like #ARTIST) will always be converted to uppercase. Same goes for empty lines in the attributes section. The current goal is to be able to parse files that adhere to the [Official Ultrastar Format Specification](https://usdx.eu/format/). For everything else, a best effort is made.

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

- Ability to backup files, for example before overwriting
- Logging
- Better error handling (and documentation of error handling)
- Metadata extraction not from txt file (e.g. song duration from audio file or video resolution from video file)

## Unplanned features

- Editing the songtext and notes
