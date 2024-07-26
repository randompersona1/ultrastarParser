# UltrastarParser

Contains methods to read or edit ultrastar files or directories.

## Installation

Use the package manager of your choice: [pypi](https://pypi.org/project/ultrastarParser/).

## Usage tips

- Make a backup of the text files. The library currently does not touch any other files. Though I try very hard to fix bugs and use the library myself, I cannot guarantee your files won't go up in flames, particularly if you are using a non-standard file structure or encoding. If something does go wrong, please file an issue.
- Certain formattings will be lost. For example, attributes (like #ARTIST) will always be converted to uppercase. Same goes for empty lines in the attributes section. The current goal is to be able to parse files that adhere to the [Official Ultrastar Format Specification](https://usdx.eu/format/). For everything else, a best effort is made.

## Features

- get and set attributes using ```UltrastarFile::get_attribute``` and ```UltrastarFile::set_attribute```. Also ```UltrastarFile::attribute_exists```
- check/validate a file for completeness, existing and correct attributes, duet parameters and karaoke possibility

```python
usf = UltrastarFile('path_to_txt_file')
check = usf.check()
faulty_attributes = usf.validate_attributes()
faulty_duet = usf.validate_duet()
faulty_urls = usf.validate_urls()
karaoke = usf.validate_karaoke()
```

- automatically reorder attributes in a file with ```UltrastarFile::reorder_auto```
- add, remove and search songs in a folder

```python
lib = Library('path_to_library')
lib.add(UltrastarFile('path_to_new_file'))
lib.remove(lib[10])
results = lib.search('#ARTIST', 'Bon Jovi')
```

- export a song list from a library in csv or json format with ```Library::export```

## Planned features

- Ability to backup files, for example before overwriting
- Logging
- Better error handling (and documentation of error handling)
- Metadata extraction not from txt file (e.g. song duration from audio file or video resolution from video file)

## Unplanned features

- Editing the songtext and notes
