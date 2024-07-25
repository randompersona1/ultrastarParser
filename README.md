# UltrastarParser

Contains methods to read or edit ultrastar files or directories.

## Installation

Use the package manager of your choice: [pypi](https://pypi.org/project/ultrastarParser/).

## Usage

1. Make a backup. Though I try very hard to fix bugs and use the library myself, I cannot guarantee your files won't go up in flames, particularly if you are using a non-standard file structure or encoding. If something does go wrong, please file an issue.

- Use `from ultrastarParser import UltrastarFile, Library` to import
- The library contains classes either for managing a single song or a library of songs.
- After editing a song, use `<UltrastarFile>.flush()` to flush changes back to the file system. Any changes made after opening/parsing will be overwritten by this.
- Certain formattings will be lost. For example, attributes (like #ARTIST) will always be converted to uppercase. The current goal is to be able to parse files that adhere to the [Official Ultrastar Format Specification](https://usdx.eu/format/). For everything else, a best effort is made.
- For the forseeable future, editing the songtext and notes is unsupported

## Planned features

- Ability to backup files, for example before overwriting
- Logging
- Better error handling
- Metadata extraction (e.g. song duration from audio file)
- Comparison between ultrastar files
- Exporting a library as json, csv with different tags included
- filtering songs in a library
