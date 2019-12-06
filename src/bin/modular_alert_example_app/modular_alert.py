import logging
from logging import handlers
import traceback
import sys
import re
import os
import json
import socket # Used for IP Address validation

try:
    from urlparse import urlparse
except:
    from urllib.parse import urlparse

try:
    basestring
except:
    basestring = str

from splunk.appserver.mrsparkle.lib.util import make_splunkhome_path

class FieldValidationException(Exception):
    pass

class Field(object):
    """
    This is the base class that should be used to for field validators. Sub-class this and override to_python if you need custom validation.
    """
    
    DATA_TYPE_STRING = 'string'
    DATA_TYPE_NUMBER = 'number'
    DATA_TYPE_BOOLEAN = 'boolean'
    
    def get_data_type(self):
        """
        Get the type of the field.
        """
        
        return Field.DATA_TYPE_STRING 
    
    def __init__(self, name, none_allowed=False, empty_allowed=True):
        """
        Create the field.
        
        Arguments:
        name -- Set the name of the field (e.g. "database_server")
        none_allowed -- Is a value of none allowed?
        empty_allowed -- Is an empty string allowed?
        """
        
        if name is None:
            raise ValueError("The name parameter cannot be none")

        if len(name.strip()) == 0:
            raise ValueError("The name parameter cannot be empty")
        
        self.name = name
        
        self.none_allowed = none_allowed
        self.empty_allowed = empty_allowed
    
    def to_python(self, value):
        """
        Convert the field to a Python object. Should throw a FieldValidationException if the data is invalid.
        
        Arguments:
        value -- The value to convert
        """
        
        if not self.none_allowed and value is None:
            raise FieldValidationException("The value for the '%s' parameter cannot be empty" % (self.name))
         
        if not self.empty_allowed and len(str(value).strip()) == 0:
            raise FieldValidationException("The value for the '%s' parameter cannot be empty" % (self.name))
        
        return value

    def to_string(self, value):
        """
        Convert the field to a string value that can be returned. Should throw a FieldValidationException if the data is invalid.
        
        Arguments:
        value -- The value to convert
        """
        
        return str(value)


class BooleanField(Field):
    
    def to_python(self, value):
        Field.to_python(self, value)
        
        if value in [True, False]:
            return value

        elif str(value).strip().lower() in ["true", "1"]:
            return True

        elif str(value).strip().lower() in ["false", "0"]:
            return False
        
        raise FieldValidationException("The value of '%s' for the '%s' parameter is not a valid boolean" % (str(value), self.name))

    def to_string(self, value):

        if value == True:
            return "1"

        elif value == False:
            return "0"
        
        return str(value)
    
    def get_data_type(self):
        return Field.DATA_TYPE_BOOLEAN
    
    
class ListField(Field):
    
    def to_python(self, value):
        
        Field.to_python(self, value)
        
        if value is not None:
            return value.split(",")
        else:
            return []
    
    def to_string(self, value):

        if value is not None:
            return ",".join(value)
        
        return ""
    
    
class RegexField(Field):
    
    def to_python(self, value):
        
        Field.to_python(self, value)
        
        if value is not None:
            try:
                return re.compile(value)
            except Exception as e:
                raise FieldValidationException(str(e))
        else:
            return None
    
    def to_string(self, value):

        if value is not None:
            return value.pattern
        
        return ""


class IntegerField(Field):
    
    def to_python(self, value):
        
        Field.to_python(self, value)
        
        if value is not None:
            try:
                return int(value)
            except ValueError as e:
                raise FieldValidationException(str(e))
        else:
            return None
    
    def to_string(self, value):

        if value is not None:
            return str(value)
        
        return ""
    
    def get_data_type(self):
        return Field.DATA_TYPE_NUMBER
    
    
class FloatField(Field):
    
    def to_python(self, value):
        
        Field.to_python(self, value)
        
        if value is not None:
            try:
                return float(value)
            except ValueError as e:
                raise FieldValidationException(str(e))
        else:
            return None
    
    def to_string(self, value):

        if value is not None:
            return str(value)
        
        return ""
    
    def get_data_type(self):
        return Field.DATA_TYPE_NUMBER

    
class RangeField(Field):

    def __init__(self, name, title, description, low, high, none_allowed=False, empty_allowed=True):
        super(RangeField, self).__init__(name, title, description, none_allowed=False, empty_allowed=True)
        self.low = low
        self.high = high
    
    def to_python(self, value):
        
        Field.to_python(self, value)
        
        if value is not None:
            try:
                tmp = int(value)
                return tmp >= self.low and tmp <= self.high
            except ValueError as e:
                raise FieldValidationException(str(e))
        else:
            return None
    
    def to_string(self, value):

        if value is not None:
            return str(value)
        
        return ""
    
    def get_data_type(self):
        return Field.DATA_TYPE_NUMBER

class URLField(Field):
    """
    Represents a URL. The URL is converted to a Python object that was created via urlparse.
    """
    
    @classmethod
    def parse_url(cls, value, name):
        parsed_value = urlparse(value)
        
        if parsed_value.hostname is None or len(parsed_value.hostname) <= 0:
            raise FieldValidationException("The value of '%s' for the '%s' parameter does not contain a host name" % (str(value), name))
        
        if parsed_value.scheme not in ["http", "https"]:
            raise FieldValidationException("The value of '%s' for the '%s' parameter does not contain a valid protocol (only http and https are supported)" % (str(value), name))
    
        return parsed_value
    
    def to_python(self, value):
        Field.to_python(self, value)
        
        return URLField.parse_url(value, self.name)
    
    def to_string(self, value):
        return value.geturl()

class DurationField(Field):
    """
    The duration field represents a duration as represented by a string such as 1d for a 24 hour period.
    
    The string is converted to an integer indicating the number of seconds.
    """
    
    DURATION_RE = re.compile("(?P<duration>[0-9]+)\s*(?P<units>[a-z]*)", re.IGNORECASE)
    
    MINUTE = 60
    HOUR   = 60 * MINUTE
    DAY    = 24 * HOUR
    WEEK   = 7 * DAY
    
    UNITS = {
             'w'       : WEEK,
             'week'    : WEEK,
             'd'       : DAY,
             'day'     : DAY,
             'h'       : HOUR,
             'hour'    : HOUR,
             'm'       : MINUTE,
             'min'     : MINUTE,
             'minute'  : MINUTE,
             's'       : 1
             }
    
    def to_python(self, value):
        Field.to_python(self, value)
        
        # Parse the duration
        m = DurationField.DURATION_RE.match(value)

        # Make sure the duration could be parsed
        if m is None:
            raise FieldValidationException("The value of '%s' for the '%s' parameter is not a valid duration" % (str(value), self.name))
        
        # Get the units and duration
        d = m.groupdict()
        
        units = d['units']
        
        # Parse the value provided
        try:
            duration = int(d['duration'])
        except ValueError:
            raise FieldValidationException("The duration '%s' for the '%s' parameter is not a valid number" % (d['duration'], self.name))
        
        # Make sure the units are valid
        if len(units) > 0 and units not in DurationField.UNITS:
            raise FieldValidationException("The unit '%s' for the '%s' parameter is not a valid unit of duration" % (units, self.name))
        
        # Convert the units to seconds
        if len(units) > 0:
            return duration * DurationField.UNITS[units]
        else:
            return duration

    def to_string(self, value):        
        return str(value)
    
class PortField(IntegerField):
    
    def to_python(self, value):
        
        v = IntegerField.to_python(self, value)
        
        if v is not None and (v < 0 or v > 65535 ):
            raise FieldValidationException("Port must be at least 0 and less than 65536")
        else:
            return v
        
class IPAddressField(Field):
    
    def to_python(self, value):
        
        v = Field.to_python(self, value)
        
        try:
            socket.inet_aton(v)
            return v
        except socket.error:
            # Not legal
            raise FieldValidationException('This IP is not a valid address, value="' + v + '"')
        

class ModularAlert(object):
    
    def __init__(self, parameters=None, logger_name='python_modular_alert', log_level=logging.INFO, log_to_file=False):
        """
        Set up the modular alert.
            
        Arguments:
        parameters -- A list of Field instances for validating the arguments
        logger_name -- The logger name to append to the logger
        log_level -- The log level of the logger
        log_to_file -- Indicates whether the log messages should be sent to a log file or just outputted to Splunk via standard output
        """
         
        if parameters is None:
            self.parameters = []
        else:
            self.parameters = parameters[:]
        
        # Check and save the logger name
        self._logger = None
        
        if logger_name is None or len(logger_name) == 0:
            raise Exception("Logger name cannot be empty")
        
        self.logger_name = logger_name
        self.log_level = log_level
        self.log_to_file = log_to_file
        self._logger = None
    
    @classmethod
    def escape_spaces(cls, s, encapsulate_in_double_quotes=False):
        """
        If the string contains spaces, then add double quotes around the string. This is useful when outputting fields and values to Splunk since a space will cause Splunk to not recognize the entire value.
        
        Arguments:
        s -- A string to escape.
        encapsulate_in_double_quotes -- If true, the value will have double-spaces added around it.
        """
        
        # Make sure the input is a string
        if s is not None:
            s = str(s)
        
        # Escape the spaces within the string (will need KV_MODE = auto_escaped for this to work)
        if s is not None:
            s = s.replace('"', '\\"')
            s = s.replace("'", "\\'")
        
        if s is not None and (" " in s or encapsulate_in_double_quotes):
            return '"' + s + '"'
        
        else:
            return s
    
    @classmethod
    def create_event_string(cls, data_dict, encapsulate_value_in_double_quotes=False):
        """
        Create a string representing the event.
        
        Argument:
        data_dict -- A dictionary containing the fields
        encapsulate_value_in_double_quotes -- If true, the value will have double-spaces added around it.
        """
        
        # Make the content of the event
        data_str = ''
        
        for k, v in data_dict.items():
            
            # If the value is a list, then write out each matching value with the same name (as mv)
            if isinstance(v, list) and not isinstance(v, basestring):
                values = v
            else:
                values = [v]
            
            k_escaped = cls.escape_spaces(k)
            
            # Write out each value
            for v in values:
                v_escaped = cls.escape_spaces(v, encapsulate_in_double_quotes=encapsulate_value_in_double_quotes)
                
                
                if len(data_str) > 0:
                    data_str += ' '
                
                data_str += '%s=%s' % (k_escaped, v_escaped)
        
        return data_str
        
    def output_event(self, data_dict, stanza, index=None, sourcetype=None, source=None, host=None, out=sys.stdout ):
        """
        Output the given event so that Splunk can see it.
        
        Arguments:
        data_dict -- A dictionary containing the fields
        stanza -- The stanza used for the input
        sourcetype -- The sourcetype
        source -- The source to use
        index -- The index to send the event to
        out -- The stream to send the event to (defaults to standard output)
        host -- The host
        """
        
        output = self.create_event_string(data_dict)
        
        out.write(output)
        out.flush()
                    
    def addParameter(self, parameter):
        """
        Add the given parameter to the list of parameters.
        
        Arguments:
        parameter -- An instance of Field that represents a parameter.
        """
        
        if self.parameters is None:
            self.parameters = []
            
        self.parameters.append(parameter)
        
    def validate(self, arguments):
        """
        Validate the arguments and return a dictionary of cleaned/converted parameters.
        
        Arguments:
        arguments -- A dictionary of arguments
        """
        
        cleaned_params = {}
        
        # Convert and check the parameters
        for name, value in arguments.items():
            
            arg_recognized = False
            
            # Go through the parameters and look for a match
            for parameter in self.parameters:
                
                # If we found a match then convert it and check it
                if parameter.name == name:
                    cleaned_params[name] = parameter.to_python(value)
                    
                    # Note that we recognized the argument
                    arg_recognized = True
                
            # Throw an exception if the argument could not be found
            if not arg_recognized:
                raise FieldValidationException("The argument '%s' is not valid" % (name))
            
        return cleaned_params
    
    def run(self, cleaned_params, payload):
        """
        Run the input using the arguments provided.
        
        Arguments:
        cleaned_params -- The arguments following validation and conversion to Python objects.
        payload -- The data from Splunk.
        out_stream -- The stream to write the output to (defaults to standard output)
        """
        
        raise Exception("Run function was not implemented")
        
    def shutdown(self):
        """
        This function is called when the modular alert should shut down.
        """
        
        pass
      
    def execute(self, in_stream=sys.stdin):
        """
        Get the arguments that were provided from the command-line and execute the script.
        
        Arguments:
        in_stream -- The stream to get the input from (defaults to standard input)
        """
        
        try:
            self.logger.debug("Execute called")
            
            # Parse input
            payload = json.loads(in_stream.read())
            
            # Validate arguments
            cleaned_params = self.validate(payload['configuration'])
            
            # Run the alert
            return self.run(cleaned_params, payload)
            
        except Exception as e:
            
            self.logger.error("Execution failed: %s", ( traceback.format_exc() ))
            
            return False
            
    @property
    def logger(self):
        
        # Make a logger unless it already exists
        if self._logger is not None:
            return self._logger
        
        logger = logging.getLogger(self.logger_name)
        logger.propagate = False # Prevent the log messages from being duplicated in the python.log file
        logger.setLevel(self.log_level)
        
        # Setup a file logger if requested
        if self.log_to_file:
            file_handler = handlers.RotatingFileHandler(make_splunkhome_path(['var', 'log', 'splunk', self.logger_name + '.log']), maxBytes=25000000, backupCount=5)
            formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        else:
            stderr_handler = logging.StreamHandler(sys.stderr)
            formatter = logging.Formatter(' %(levelname)s %(message)s')
            stderr_handler.setFormatter(formatter)
            logger.addHandler(stderr_handler)
        
        self._logger = logger
        return self._logger
    
    @logger.setter
    def logger(self, logger):
        self._logger = logger