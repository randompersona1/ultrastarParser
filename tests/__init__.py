from ultrastarParser import UltraStarFile

if __name__ == '__main__':
    usf = UltraStarFile('tests/ABBA - Dancing Queen.txt')
    print(usf.get_attribute('#ARTIST'))
    print(usf.get_attribute('#TITLE'))

    usf.set_attribute('#ARTIST', 'Bon Jovi')
    print(usf.get_attribute('#ARTIST'))

    usf.set_attribute('#COVER', 'ABBA - Dancing Queen.jpg')
    print(usf.get_attribute('#COVER'))

    usf.reorder_auto()