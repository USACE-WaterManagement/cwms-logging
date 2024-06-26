#!/bin/env python

import os
import time
import re
import logging
import argparse
import sys
cwms_home = os.getenv('CWMS_HOME')
sys.path.append("{}/bin/lib".format(cwms_home))
sys.path.append("{}/bin".format(cwms_home))
print("$CWMS_HOME/bin and $CWMS_HOME/bin/lib added to sys.path. New path: {}".format(sys.path))
from loggingSetup import setup_logging
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class MyHandler(FileSystemEventHandler):
    def __init__(self, directory, pattern):
        self.directory = directory
        self.pattern = pattern
        self.files = {}

    def on_any_event(self, event):
        logging.getLogger("logWatcher.py").debug("Event: %s" % event)
        if not event.is_directory and re.match(self.pattern, os.path.split(event.src_path)[-1]):
            if event.src_path not in self.files:
                self.files[event.src_path] = open(event.src_path, 'r')
                self.files[event.src_path].seek(0, os.SEEK_END)
            logger = logging.getLogger("logWatcher.py " + os.path.split(event.src_path)[-1])
            for line in self.files[event.src_path]:
                logger.info(line.strip())


def parse_arguments():
    parser = argparse.ArgumentParser(description='Monitor log file and send new lines to the Graylog server.')
    parser.add_argument('directory', help='Directory to monitor.')
    parser.add_argument('pattern', help='Filename pattern.')
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    setup_logging()
    event_handler = MyHandler(args.directory, args.pattern)
    observer = Observer()
    observer.schedule(event_handler, path=args.directory, recursive=False)
    logging.getLogger("logWatcher.py").debug("Started watching: %s" % args.directory)
    observer.start()

    SLEEP_LOOP_SECONDS = 1
    try:
        while True:
            time.sleep(SLEEP_LOOP_SECONDS)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
