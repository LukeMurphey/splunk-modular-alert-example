
import unittest
import errno
import sys
import os
import re

sys.path.append( os.path.join("..", "src", "bin") )
sys.path.append( os.path.join("..", "src", "bin", "modular_alert_example_app") )

from modular_alert_example_app.modular_alert import ModularAlert, Field, IntegerField, FieldValidationException

class TestModularAlert(unittest.TestCase):
    """
    Test the universal forwarder module that provides some generic helpers in case Splunk's
    libraries are not available (like on Universal Forwarders which lack Splunk's Python).
    """

    def test_construct(self):
        """
        Make sure the modular alert can be constructed.
        """
        mod_alert = ModularAlert()
        self.assertIsNotNone(mod_alert)

    # escape_spaces
    # create_event_string

if __name__ == "__main__":
    unittest.main()
