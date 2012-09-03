import re

from vinge.stop_words import STOP_WORDS

class TokenType:
    """"
    Type of a token. Tag is a normal word, id is something special that one
    wants to pay more attention to.
    """
    TAG = 1,
    ID = 2

ID_TOKEN_REGEXES = [
    # UUIDs
    # Example: 2cdd3a76-78fb-412b-bcf2-f09c3b0d9670
    re.compile('^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$'),
    # urns
    # Example: urn:foo:bar/baz
    re.compile('^urn:[^\s]+$')
    ]

def is_token_id(string):
    # TODO(trevor) - make this configurable
    # IDs for now are UUIDs or anything that is a urn
    # UUID string representation
    for regex in ID_TOKEN_REGEXES:
        if regex.match(string):
            return True
    return False

def is_token_tag(string):
    return (not is_token_id(string)) and (not is_stop_word(token))

def is_stop_word(string):
    return string in STOP_WORDS

def tokenize(string):
    """
    Takes a string and returns a list of the tokens found in that string.

    Args:
        string (str)
    Returns:
        list of (str, TokenType)
    """
    ret = []
    # For now we tokenize based upon space
    tokens = string.split()
    for token in tokens:
        if is_token_id(token):
            token_type = TokenType.ID
        elif is_stop_word(token):
            continue
        else:
            token_type = TokenType.TAG
        ret.append((token, token_type))
    return ret
