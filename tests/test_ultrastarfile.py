import unittest
from ultrastarParser import UltrastarFile


class TestUltraStarFile(unittest.TestCase):
    def setUp(self):
        self.usf = UltrastarFile('tests/resources/ABBA - Dancing Queen.txt')

    def test_set_attribute(self):
        self.usf.set_attribute('#ARTIST', 'Bon Jovi')
        self.usf.flush()
        self.assertEqual(self.usf.get_attribute('#ARTIST'), 'Bon Jovi')

    def test_reorder(self):
        self.usf.reorder_attribute('#YEAR', 0)
        self.usf.flush()
        self.assertEqual(self.usf.attributes[0], ['#YEAR', '1976'])

    def test_reorder_auto(self):
        self.usf.reorder_auto()
        self.usf.flush()
        self.assertEqual(self.usf.attributes[0], ['#ARTIST', 'ABBA'])
        self.assertEqual(self.usf.attributes[1], ['#TITLE', 'Dancing Queen'])


if __name__ == '__main__':
    unittest.main()
