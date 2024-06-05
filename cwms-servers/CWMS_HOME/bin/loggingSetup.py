#  Copyright (c) 2024
#  United States Army Corps of Engineers - Hydrologic Engineering Center (USACE/HEC)
#  All Rights Reserved.  USACE PROPRIETARY/CONFIDENTIAL.
#  Source may not be released without written approval from HEC

import json
import logging
import logging.config
import os
import sys


def setup_logging():
    cwms_home = os.getenv('CWMS_HOME')
    if (cwms_home == None):
        (logging.getLogger("logging_setup")
         .warning("Could not load python logging config. CWMS_HOME not defined."))
    else:
        path = cwms_home + '/config/system_config/logging_config.json'
        with open(path, 'r') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
        logging.getLogger("logging_setup").debug("Loaded logging config: " + path)


def reroute_std_out_error():
    class LoggerWriter:
        def __init__(self, level, origin):
            # Map logging module levels to method names
            self._level = level
            self._origin = origin

        def write(self, message):
            self._origin.write(message)
            # Remove line breaks
            if message != '\n':
                logging.log(self._level, message.rstrip())

        def flush(self):
            pass

    # Redirect stdout and stderr to logging
    sys.stdout = LoggerWriter(logging.INFO, sys.stdout)
    sys.stderr = LoggerWriter(logging.ERROR, sys.stderr)
