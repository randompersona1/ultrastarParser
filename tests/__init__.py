from ultrastarparser import Song, Library


def test_song():
    song = Song(
        "C:\\Users\\Simon\\Coding\\Python Scripts\\ultrastar\\ultrastarParser\\tests\\4 Non Blondes - What's Up.txt"
    )
    print(song.get_attribute("AUDIO"))
    print(song.get_version())
    song.set_version("0.1.0")
    print(song.get_version())
    song.flush()

    lib = Library(
        "C:\\Users\\Simon\\Coding\\Python Scripts\\ultrastar\\ultrastarParser\\tests"
    )
    for song in lib:
        print(song.get_attribute("TITLE"))
    lib.export("C:\\Users\\Simon\\Desktop\\t.json", "json")
    print(lib.search("TITLE", "What’s Up?"))


if __name__ == "__main__":
    test_song()
