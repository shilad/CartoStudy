import codecs
import os
from collections import defaultdict
import json

import sys


class LogError(Exception):
    def __init__(self, line, message):
        self.line = line
        self.message = message

    def __str__(self):
        return 'Log Error - %s: %s' % (self.message, repr(self.line))


class LogRecord:
    def __init__(self, line):
        tokens = line.split('\t')
        if len(tokens) != 6:
            raise LogError(line, 'invalid number of tokens (%d)' % len(tokens))

        self.line = line
        self.tstamp = float(tokens[0])      # seconds since the epoch
        self.workerId = tokens[1]           # Worker id or None
        self.url = tokens[2]                # Full URL
        self.event = tokens[3]              # Event: 'code', 'map', or 'page
        self.info = json.loads(tokens[4])   # Event specific info
        self.params = defaultdict(list)     # query param -> list of values for param

        if self.workerId is 'None':
            self.workerId = None
        for k, v in json.loads(tokens[5]):
            self.params[k].append(v)

def read_log(dir):
    for filename in os.listdir(dir):
        for line in codecs.open(dir + '/' + filename, encoding='utf-8'):

            # Hack: One turker had a tab in their worker id:
            line = line.replace(' AQP74RCFA4CF8 \t', 'AQP74RCFA4CF8')
            line = line.replace('AQP74RCFA4CF8+\t', 'AQP74RCFA4CF8+')

            try:
                yield LogRecord(line)
            except LogError as e:
                sys.stderr.write(str(e) + '\n')

if __name__ == '__main__':
    for record in read_log('logs/prod'):
        print record.tstamp, record.workerId, record.event, record.info
