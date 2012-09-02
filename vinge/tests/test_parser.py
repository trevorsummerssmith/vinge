import vinge
from vinge.vertex import LogLineVertex
from vinge.parser import *


from datetime import datetime

class TestParser:

    def test__parse_log_line_success(self):
        line = "2012-09-01 03:21:20,305 INFO  [MyThread9] c.g.o.a.FooBarBaz : This is my log message ok"
        (dt, thread_id, msg) = vinge.parser._parse_log_line(line)
        dt_answer = datetime(year=2012, month=9, day=1, hour=3, minute=21, second=20, microsecond=305000)
        assert dt == dt_answer
        assert thread_id == 'MyThread9'
        assert msg == ' c.g.o.a.FooBarBaz : This is my log message ok'

    def test__parse_log_line_failure(self):
        ret = vinge.parser._parse_log_line("hello")
        assert ret == None

    def test_parse_log_one_line_no_ids(self):
        lines = ["2012-09-01 03:21:20,305 INFO  [MyThread9] foo\n"]
        (vertices, tag_map, id_map) = parse_log(lines)

        # Build up vertex for answer
        dt = datetime(year=2012, month=9, day=1, hour=3, minute=21, second=20, microsecond=305000)
        vertex = LogLineVertex(lines[0].rstrip(), ' foo', 0, 'MyThread9', dt)
        assert len(vertices) == 1
        assert vertices == [vertex]

        # tag map should have one entry
        assert tag_map == {'foo' : [vertex]}

        # id map should be empty
        assert id_map == {}

    def test_parse_log_two_lines_same_tokens(self):
        lines = ["2012-09-01 03:21:20,305 INFO  [MyThread9] foo\n",
                 "2012-09-01 03:21:20,305 INFO  [MyThread10] bar foo\n"
                 ]
        (vertices, tag_map, id_map) = parse_log(lines)

        # Build up vertices for answer
        dt1 = datetime(year=2012, month=9, day=1, hour=3, minute=21, second=20, microsecond=305000)
        vertex1 = LogLineVertex(lines[0].rstrip(), ' foo', 0, 'MyThread9', dt1)
        dt2 = datetime(year=2012, month=9, day=1, hour=3, minute=21, second=20, microsecond=305000)
        vertex2 = LogLineVertex(lines[1].rstrip(), ' bar foo', 0, 'MyThread10', dt2)

        assert len(vertices) == 2
        assert vertices == [vertex1, vertex2]

        # tag map should have two entries
        assert tag_map == {'foo' : [vertex1, vertex2],
                           'bar' : [vertex2]}

        # id map should be empty
        assert id_map == {}

    def test_parse_log_two_lines_same_tokens_plus_ids(self):
        lines = ["2012-09-01 03:21:20,305 INFO  [MyThread9] urn:bar foo bf09c8a0-f54a-11e1-a21f-0800200c9a66\n",
                 "2012-09-01 03:21:20,305 INFO  [MyThread10] bar foo urn:bar\n"
                 ]
        (vertices, tag_map, id_map) = parse_log(lines)

        # Build up vertices for answer
        dt1 = datetime(year=2012, month=9, day=1, hour=3, minute=21, second=20, microsecond=305000)
        vertex1 = LogLineVertex(lines[0].rstrip(), ' foo', 0, 'MyThread9', dt1)
        dt2 = datetime(year=2012, month=9, day=1, hour=3, minute=21, second=20, microsecond=305000)
        vertex2 = LogLineVertex(lines[1].rstrip(), ' bar foo urn:bar', 0, 'MyThread10', dt2)

        assert len(vertices) == 2
        assert vertices == [vertex1, vertex2]

        # tag map should have two entries
        assert tag_map == {'foo' : [vertex1, vertex2],
                           'bar' : [vertex2]}

        # id map should be empty
        assert id_map == {'urn:bar' : [vertex1, vertex2],
                          'bf09c8a0-f54a-11e1-a21f-0800200c9a66' : [vertex1]}
