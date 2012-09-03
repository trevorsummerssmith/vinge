from datetime import datetime

from vinge.graph import make_graph
from vinge.vertex import LogLineVertex, TagVertex, UniqueIDVertex

def time_weighting(t1, t2):
    return 1.0

def assert_lists_equal(list1, list2):
    assert sorted(list1) == sorted(list2)

class TestGraph:

    def test_graph_with_one_line(self):
        # One vertex
        lines = ["2012-09-01 03:21:20,305 INFO  [MyThread9] foo\n"]
        dt1 = datetime(year=2012, month=9, day=1, hour=3, minute=21, second=20, microsecond=305000)
        vertex = LogLineVertex(lines[0].rstrip(), ' foo', 0, 'MyThread9', dt1)
        tag_map = {'foo' : [vertex]}
        id_map = {}

        # Make graph and check its structure
        graph = make_graph([vertex], tag_map, id_map, time_weighting)
        tag_vertex = TagVertex('foo',  dt1)
        assert len(graph.nodes()) == 2
        assert_lists_equal(graph.nodes(), [vertex, tag_vertex])
        assert_lists_equal(graph.edges(data=True),
                           [(vertex, tag_vertex, {'weight' : 1.0}),
                            (tag_vertex, vertex, {'weight' : 1.0})])

    def test_graph_with_two_lines_share_tag(self):
        lines = ["2012-09-01 03:21:20,305 INFO  [MyThread9] foo\n",
                 "2012-09-01 03:22:20,305 INFO  [MyThread10] foo\n"]
        dt1 = datetime(year=2012, month=9, day=1, hour=3, minute=21, second=20, microsecond=305000)
        vertex1 = LogLineVertex(lines[0].rstrip(), ' foo', 0, 'MyThread9', dt1)
        dt2 = datetime(year=2012, month=9, day=1, hour=3, minute=22, second=20, microsecond=305000)
        vertex2 = LogLineVertex(lines[1].rstrip(), ' foo', 1, 'MyThread10', dt2)
        tag_map = {'foo' : [vertex1, vertex2]}
        id_map = {}

        # Make graph and check its structure
        graph = make_graph([vertex1, vertex2], tag_map, id_map, time_weighting)
        tag_vertex1 = TagVertex('foo', dt1)
        tag_vertex2 = TagVertex('foo', dt2)
        assert len(graph.nodes()) == 4
        assert_lists_equal(graph.nodes(), [vertex1, vertex2, tag_vertex1, tag_vertex2])
        edges = graph.edges(data=True)
        assert len(edges) == 8
        # The edge weights are normalized so that they sum to 1
        assert_lists_equal(edges,
                           # Log line to tag edges
                           [(vertex1, tag_vertex1, {'weight' : 0.5}),
                            (tag_vertex1, vertex1, {'weight' : 0.5}),
                            (vertex2, tag_vertex2, {'weight' : 0.5}),
                            (tag_vertex2, vertex2, {'weight' : 0.5}),
                            # Tag to tag edges
                            (tag_vertex1, tag_vertex2, {'weight' : 0.5}),
                            (tag_vertex2, tag_vertex1, {'weight' : 0.5}),
                            # Log line to log line edges
                            (vertex1, vertex2, {'weight' : 0.5}),
                            (vertex2, vertex1, {'weight' : 0.5})])

    def test_graph_with_two_lines_share_id(self):
        lines = ["2012-09-01 03:21:20,305 INFO  [MyThread9] urn:9\n",
                 "2012-09-01 03:22:20,305 INFO  [MyThread10] urn:9\n"]
        dt1 = datetime(year=2012, month=9, day=1, hour=3, minute=21, second=20, microsecond=305000)
        vertex1 = LogLineVertex(lines[0].rstrip(), ' urn:9', 0, 'MyThread9', dt1)
        dt2 = datetime(year=2012, month=9, day=1, hour=3, minute=22, second=20, microsecond=305000)
        vertex2 = LogLineVertex(lines[1].rstrip(), ' urn:9', 1, 'MyThread10', dt2)
        tag_map = {}
        id_map = {'urn:9' : [vertex1, vertex2]}

        # Make graph and check its structure
        graph = make_graph([vertex1, vertex2], tag_map, id_map, time_weighting)
        id_vertex = UniqueIDVertex('urn:9')
        assert len(graph.nodes()) == 3
        assert_lists_equal(graph.nodes(), [vertex1, vertex2, id_vertex])
        edges = graph.edges(data=True)
        assert len(edges) == 6
        # The edge weights are normalized so that they sum to 1
        assert_lists_equal(edges,
                           [(vertex1, id_vertex, {'weight' : 0.5}),
                            (id_vertex, vertex1, {'weight' : 0.5}),
                            (vertex2, id_vertex, {'weight' : 0.5}),
                            (id_vertex, vertex2, {'weight' : 0.5}),
                            # Log line to log line edges
                            (vertex1, vertex2, {'weight' : 0.5}),
                            (vertex2, vertex1, {'weight' : 0.5})
                            ])
