from ultrastarParser import UltraStarFile

if __name__ == '__main__':
    usf = UltraStarFile('tests/ABBA - Dancing Queen.txt')
    usf.set_attribute('#ARTIST', 'Bon Jovi')

    usf.reorder_auto()
    usf.flush()
    print()