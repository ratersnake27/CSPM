import unittest
from cspm import find_pokemon_id, get_team_id, get_team_name

# Run with: python3 unit_test.py
class TestCSPM(unittest.TestCase):

    def test_valid_pokemon(self):
        self.assertEqual(find_pokemon_id('Bulbasaur'), 1)
        self.assertEqual(find_pokemon_id('Ho-Oh'), 250)
        self.assertEqual(find_pokemon_id('Lugia'), 249)
        self.assertEqual(find_pokemon_id('Egg'), 0)

    def test_invalid_pokemon(self):
        self.assertEqual(find_pokemon_id('missingno'), 0)
        self.assertEqual(find_pokemon_id('bulbasaur'), 0)
        self.assertEqual(find_pokemon_id('ho-Oh'), 0)
        self.assertEqual(find_pokemon_id('egg'), 0)

    def test_get_team_id(self):
        self.assertEqual(get_team_id("0"), 0)
        self.assertEqual(get_team_id("1"), 1)
        self.assertEqual(get_team_id("2"), 2)
        self.assertEqual(get_team_id("3"), 3)
        self.assertEqual(get_team_id("4"), 0)

        self.assertEqual(get_team_id("Mystic"), 1)
        self.assertEqual(get_team_id("Valor"), 2)
        self.assertEqual(get_team_id("Instinct"), 3)

        self.assertEqual(get_team_id("mystic"), 1)
        self.assertEqual(get_team_id("Blue"), 1)
        self.assertEqual(get_team_id("blue"), 1)

        self.assertEqual(get_team_id("blah"), 0)

    def test_get_team_name(self):
        self.assertEqual(get_team_name(0), 'Unknown')
        self.assertEqual(get_team_name(1), 'Mystic')
        self.assertEqual(get_team_name(2), 'Valor')
        self.assertEqual(get_team_name(3), 'Instinct')
        self.assertEqual(get_team_name(4), 'Unknown')

if __name__ == '__main__':
    unittest.main()
