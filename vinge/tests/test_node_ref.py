from vinge.node_ref import NodeRefType, NodeRef, parse_node_ref

class TestNodeRef:
    def test_current(self):
        node_ref = parse_node_ref("current")
        assert node_ref == NodeRef(NodeRefType.CURRENT)

    def test_cur(self):
        node_ref = parse_node_ref("cur")
        assert node_ref == NodeRef(NodeRefType.CURRENT)

    def test_cur_eq_current(self):
        node_ref1 = parse_node_ref("cur")
        node_ref2 = parse_node_ref("current")
        assert node_ref1 == node_ref2

    def test_neighbors(self):
        node_ref = parse_node_ref("cur.neighbors[1]")
        assert node_ref == NodeRef(NodeRefType.NEIGHBOR, neighbor_index=1)

    def test_nbrs(self):
        node_ref = parse_node_ref("cur.nbrs[9]")
        assert node_ref == NodeRef(NodeRefType.NEIGHBOR, neighbor_index=9)

    def test_fail_cur_neighbors_no_period(self):
        node_ref = parse_node_ref("curneighbors[0]")
        assert node_ref == None

    def test_fail_neighbors_with_no_integer(self):
        node_ref = parse_node_ref("cur.neighbors[a]")
        assert node_ref == None

    def test_fail_dog(self):
        # dog is not a node ref
        node_ref = parse_node_ref("dog")
        assert node_ref == None
