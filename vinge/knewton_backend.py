import re

import tokens
from datetime import datetime
from tokens import TokenType
from vertex import LogLineVertex
from backends import BackEnd

class KnewtonBackEnd(BackEnd):
    def parse_line_into_vertex_and_msg(self, line):
        """
        Args:
            line (str)
        Returns:
            vertex or None if the line doesn't match
        """
        # TODO(trevor) need to make this configurable
        # Example log line:
        # 2012-09-01 00:00:20,305 INFO  [MyThread9] c.g.o.a.FooBarBaz : This is my log message ok
        # group 1 - year
        #       2 - month
        #       3 - day
        #       4 - hour
        #       5 - minute
        #       6 - second
        #       7 - millisecond
        # group 8 - log level
        # group 9 - thread id
        # group 10 - rest of the log line
        # Python caches the regex internally.
        regex = re.compile('^(\d\d\d\d)-(\d\d)-(\d\d) (\d\d):(\d\d):(\d\d),(\d\d\d)\s+(\w+)\s+\[(\w+)\](.+)$')
        m = regex.match(line)
        if not m:
            return None
        # python datetime object has microseconds, not millis, which is why we
        # are grabbing the constituent parts of the date instead of using strptime
        microseconds = int(m.group(7))*1000
        dt = datetime(year=int(m.group(1)),
                      month=int(m.group(2)),
                      day=int(m.group(3)),
                      hour=int(m.group(4)),
                      minute=int(m.group(5)),
                      second=int(m.group(6)),
                      microsecond=microseconds)

        thread_id = m.group(9)
        msg = m.group(10)
        
        return LogLineVertex(line, msg, self.line_number, thread_id, dt), msg

    def tokenize_msg(self, msg):
        return tokens.tokenize(msg)



