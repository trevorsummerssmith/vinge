from kct.color import *

from tokens import TokenType
from tokens import tokenize

from vertex import LogLineVertex
from vertex import TagVertex
from vertex import UniqueIDVertex

def shorten_color_str(string, len):
    """
    Shortens string to len provided. Ends with a default white text
    and black background.

    Args:
        string (str)
        len (int)

    Returns: str
    """
    # TODO(trevor) this is quick for now. it should actually only remove
    # only printable characters
    return "%s%s" % (string[:len-1], default(''))

def format_id(string):
    return red(string, attrs='bold')

def format_tag(string):
    return cyan(string)

def format_vertex(vertex):
    """
    Helper method that switches on the type of vertex and selects the format
    function.

    Args:
        vertex(subclass of vertex.Vertex)

    Returns: str
    """
    if isinstance(vertex, LogLineVertex):
        return format_log_line_vertex(vertex)
    elif isinstance(vertex, UniqueIDVertex):
        return format_unique_id_vertex(vertex)
    elif isinstance(vertex, TagVertex):
        return format_tag_vertex(vertex)
    # else ... broken type system.
    return ''

def format_log_line_vertex(vertex):
    """
    Formats the log line as a string with ids and tags highlighted.

    Args:
        vertex (vertex.LogLineVertex)

    Returns: str
    """
    msg = ""
    # Tokenize the message
    for (token, token_type) in tokenize(vertex.message):
        fmt = token
        if token_type is TokenType.TAG:
            fmt = format_tag(fmt)
        elif token_type is TokenType.ID:
            fmt = format_id(fmt)
        msg += '%s' % fmt

    # Rebuild the log message now
    ret = "%s [%s] %s" % (vertex.time, format_tag(vertex.thread_id), msg)

    return ret

def format_tag_vertex(vertex):
    """
    Formats tag vertex as the tag highlighed with the date

    Args:
        vertex (vertex.TagVertex)

    Returns: str
    """
    return "%s %s" % (format_tag(vertex.word), vertex.time)

def format_unique_id_vertex(vertex):
    """
    Formats unique id vertex as the id highlighted

    Args:
        vertex (vertex.UniqueIdVertex)

    Returns: str
    """
    return format_id(vertex.id)
