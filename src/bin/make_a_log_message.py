import logging
import sys
from modular_alert_example_app.modular_alert import ModularAlert, Field, IntegerField, FieldValidationException

class MakeLogMessageAlert(ModularAlert):
    """
    This alert just makes a log message (its an example).
    """
    
    def __init__(self, **kwargs):
        params = [
                    IntegerField("importance"),
                    Field("message")
        ]
        
        super(MakeLogMessageAlert, self).__init__(params, logger_name="make_a_log_message_alert", log_level=logging.INFO )

    def run(self, cleaned_params, payload):
        pass