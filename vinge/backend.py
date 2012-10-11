from vinge.tokens import TokenType
from vinge.vertex import LogLineVertex, TagVertex, UniqueIDVertex
from vinge.format import format_tag, format_id, shorten_color_str

def _dict_map(dictionary, fn):
    for (k,v) in dictionary.iteritems():
        dictionary[k] = fn(v)

class BackEnd(object):
    def __init__(self, stop_words, ids):
        self.line_number = 0
        self.line_vertices = []
        self.tag_map = {}
        self.id_map = {}

    def parse_file_into_line_generator(self, fname):
        file = open(filename, 'r')
        for line in file:
            yield line            

    def parse_line_into_vertex_and_msg(self, line):
        raise NotImplementedError

    def tokenize_msg(self, msg):
        raise NotImplementedError

    def parse_file(self, filename):
        for line in self.parse_file_into_line_generator(filename):
            line = line.rstrip()

            # 1 Create log line vertex for each line
            vertex, msg = self.parse_line_into_vertex_and_msg(line)
            # TODO(trevor) for now skip non conforming lines
            if vertex is None:
                continue # or raise parse error??
            self.line_vertices.append(vertex)
            self.line_number += 1

            # 2 Look for tokens, then create separate tag and id maps
            # Each map is from token to list of associated vertices
            tokens = self.tokenize_msg(msg)
            for (token, token_type) in tokens:
                if token_type == TokenType.TAG:
                    this_map = self.tag_map
                elif token_type == TokenType.ID:
                    this_map = self.id_map
                else:
                    # skip stop words and spaces
                    continue
                # We use a set here so that a line which has a word more than once
                # doesn't get counted twice
                this_set = this_map.get(token, set())
                this_set.add(vertex)
                this_map[token] = this_set

        # Turn the sets back to lists
        _dict_map(self.tag_map, lambda s:list(s))
        _dict_map(self.id_map, lambda s:list(s))

        return self.line_vertices, self.tag_map, self.id_map

    def format_log_line_vertex(self, vertex):
        msg = ""
        # Tokenize the message
        for (token, token_type) in self.tokenize_msg(vertex.message):
            fmt = token
            if token_type is TokenType.TAG:
                fmt = format_tag(fmt)
            elif token_type is TokenType.ID:
                fmt = format_id(fmt)
            msg += '%s ' % fmt

        # Rebuild the log message now
        ret = "%s [%s] %s" % (vertex.time, format_tag(vertex.thread_id), msg)

        return ret

    def format_tag_vertex(self, vertex):
        """
        Formats tag vertex as the tag highlighed with the date

        args:
            vertex (vertex.TagVertex)

        Returns: str
        """
        return "%s %s" % (format_tag(vertex.word), vertex.time)

    def format_unique_id_vertex(self, vertex):
        """
        Formats unique id vertex as the id highlighted

        Args:
            vertex (vertex.UniqueIdVertex)

        Returns: str
        """
        return format_id(vertex.id)

    def format_vertex(self, vertex):
        """
        Helper method that switches on the type of vertex and selects the format
        function.

        Args:
            vertex(subclass of vertex.Vertex)

        Returns: str
        """
        if isinstance(vertex, LogLineVertex):
            return self.format_log_line_vertex(vertex)
        elif isinstance(vertex, UniqueIDVertex):
            return self.format_unique_id_vertex(vertex)
        elif isinstance(vertex, TagVertex):
            return self.format_tag_vertex(vertex)
        # else ... broken type system.
        return ''
