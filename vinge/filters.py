from vertex import NodeKind

"""
Default filter functions used by regexes.

N.b. the tag/logline/id functions share the name of BaseType elements
in the regex language (see regex_parser for more information).

It is important not only that these methods stay here, but that their names
stay the same, because the name of these methods is used to print out the
regexes. If the name of the method changed, then when we print out the regex
it would no longer be a valid regex. So, be sure to edit this file when updating
the regex language parser code.
"""

def tag(v):
    # IMPORTANT See module comments before editing this
    if v.kind == NodeKind.NodeKindTagVertex:
        return 1.0
    else:
        return 0.0

def logline(v):
    # IMPORTANT See module comments before editing this
    if v.kind == NodeKind.NodeKindLogLineVertex:
        return 1.0
    else:
        return 0.0

def id(v):
    # IMPORTANT See module comments before editing this
    if v.kind == NodeKind.NodeKindUniqueIDVertex:
        return 1.0
    else:
        return 0.0

def number_of_es(v):
    if v.kind == NodeKind.NodeKindLogLineVertex:
        return v.message.lower().count('e')
    elif v.kind == NodeKind.NodeKindUniqueIDVertex:
        return 0.0
    elif v.kind == NodeKind.NodeKindTagVertex:
        return v.word.lower().count('e')
