import re

from datetime import datetime

from tokens import tokenize
from tokens import TokenType
from vertex import LogLineVertex

def parse_log_file(filename):
    file = open(filename, 'r')
    return parse_log(file)

def _parse_log_line(line):
    """
    Args:
        line (str)
    Returns:
        (datetime, str, str) (time, thread id, log message)
        or None if the line doesn't match
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
    return (dt, m.group(9), m.group(10))

def parse_log(lines):
    """
    Args:
      lines (iterable of str) Assumes the trailing newline is part of the line

    Returns:
       (list of LogLineVertex,
        dict(str -> list of LogLineVertex),
        dict(str -> list of LogLineVertex))
        List of the actual log line vertices,
        dict from tags to the vertices that have it,
        dict from ids to the vertices that have it
    """
    log_lines = []
    tag_map = {}
    id_map = {}
    line_number = 0
    for line in lines:
        line = line.rstrip()
        ret = _parse_log_line(line)
        # TODO(trevor) for now skip non conforming lines
        if ret is None:
            line_number += 1
            continue
        (dt, thread_id, msg) = ret

        # 1 Create log line vertex for each line
        vertex = LogLineVertex(line, msg, line_number, thread_id, dt)
        log_lines.append(vertex)

        # 2 Look for tokens, then create separate tag and id maps
        # Each map is from token to list of associated vertices
        tokens = tokenize(msg)
        for (token, token_type) in tokens:
            if token_type == TokenType.TAG:
                this_map = tag_map
            else:
                this_map = id_map
            this_list = this_map.get(token, [])
            this_list.append(vertex)
            this_map[token] = this_list
        line_number += 1
    return (log_lines, tag_map, id_map)

if __name__ == '__main__':
    import sys
    parse_log_file(sys.argv[1])
