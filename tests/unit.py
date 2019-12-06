
import unittest
import errno
import sys
import os
import re

sys.path.append( os.path.join("..", "src", "bin") )
sys.path.append( os.path.join("..", "src", "bin", "modular_alert_example_app") )

from modular_alert_example_app.modular_alert import ModularAlert, URLField

class TestModularAlert(unittest.TestCase):
    """
    Test the ability to construct the modular alert.
    """

    def test_construct(self):
        """
        Make sure the modular alert can be constructed.
        """
        mod_alert = ModularAlert()
        self.assertIsNotNone(mod_alert)

    def test_create_event_string(self):
        """
        Make sure event string can be created.
        """
        self.assertEqual(ModularAlert.create_event_string({'a' : 'A'}), "a=A")
        self.assertEqual(ModularAlert.create_event_string({'a' : ['A', 'a']}), "a=A a=a")

class TestURLField(unittest.TestCase):
    """
    Test the ability to construct the modular alert.
    """

    def test_parse_url(self):
        parsed_url = URLField.parse_url('https://localhost', 'url')

        self.assertIsNotNone(parsed_url)

    # escape_spaces
    # create_event_string

if __name__ == "__main__":
    unittest.main()
