import ultrastarparser.song


def test_song():
    song = ultrastarparser.song.Song(
        "C:\\Users\\Simon\\Vocaluxe\\Songs\\ABBA - S.O.S.txt"
    )
    print(song.get_attribute("AUDIO"))
    print(song.get_version())
    song.set_version("2.0.0")
    print(song.get_version())
    song.flush()


if __name__ == "__main__":
    test_song()
