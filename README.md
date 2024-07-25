# UltrastarParser

Contains methods to read or edit ultrastar files or directories.

Not yet implemented:

- Auto-detecting duet
- Auto-detecting missing information including files, previewstart, language, genre

## Installation

Use the package manager of your choice: [pypi](https://pypi.org/project/ultrastarParser/)

## Usage

1. Make a backup. Though I try very hard, I cannot guarantee your files won't go up in flames. If something does go wrong, please file an issue.

- The library contains classes either for managing a single song or a library of songs.
- After editing a song, use `<UltraStarFile>.flush()` to flush changes back to the file system. Any changes made after opening/parsing will be overwritten by this.
- Certain formattings will be lost. For example, attributes (like #ARTIST) will always be converted to uppercase. The current goal is to be able to parse files that adhere to the [Official Ultrastar Format Specification](https://usdx.eu/format/)
- For the forseeable future, editing the songtext and notes is unsupported

## Planned features

- Validation of attribute values: Ensure that certain attributes have valid values (e.g., #BPM should be a positive number).
- Ability to backup files, for example before overwriting
- Logging
- Better error handling
- Metadata extraction (e.g. song duration from audio file)
- Comparison between ultrastar files
