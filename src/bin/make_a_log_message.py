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

    def make_the_log_message(self, message, importance):
        """
        This is the function that does what this modular alert is supposed to do.
        """
        self.logger.info("message=%s, importance=%i", message, importance)

    def run(self, cleaned_params, payload):
        
        # Get the information we need to execute the alert action
        importance = cleaned_params.get('importance', 0)
        message = cleaned_params.get('message', "(blank)")
        
        self.logger.info("Ok, here we go...")
        self.make_the_log_message(message, importance)
        self.logger.info("Successfully executed the modular alert. You are a total pro.")
        
        
"""
If the script is being called directly from the command-line, then this is likely being executed by Splunk.
"""
if __name__ == '__main__':
    
    # Make sure this is a call to execute
    if len(sys.argv) > 1 and sys.argv[1] == "--execute":
        
        try:
            modular_alert = MakeLogMessageAlert()
            modular_alert.execute()
            sys.exit(0)
        except Exception as e:
            print >> sys.stderr, "Unhandled exception was caught, this may be due to a defect in the script:" + str(e) # This logs general exceptions that would have been unhandled otherwise (such as coding errors)
            raise
        
    else:
        print >> sys.stderr, "Unsupported execution mode (expected --execute flag)"
        sys.exit(1)