import re

from vinge.stop_words import STOP_WORDS

class TokenType:
    """"
    Type of a token. Tag is a normal word, id is something special that one
    wants to pay more attention to.
    """
    TAG = 1,
    ID = 2,
    STOP_WORD = 3,
    # Set of characters we use to tokenize. Space, comma, equals, etc.
    SPLITTER = 4

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
    return (not is_token_id(string)) and (not is_stop_word(string))

def is_stop_word(string):
    return string in STOP_WORDS

def is_splitter(string):
    return re.match('[\s=,]+', string) is not None

def default_tokenize(string):
    """
    Takes a string and returns a list of the tokens found in that string.

    Args:
        string (str)
    Returns:
        list of (str, TokenType)
    """
    ret = []
    # TODO make sure you keep this in-sync with the is_splitter method above
    tokens = re.split('([\s=,]+)', string)
    # There can be empty strings at the beginning of the line from that
    for token in tokens:
        # Throw away first empty guy
        if token == '':
            continue
        if is_token_id(token):
            token_type = TokenType.ID
        elif is_stop_word(token):
            token_type = TokenType.STOP_WORD
        elif is_splitter(token):
            token_type = TokenType.SPLITTER
        else:
            token_type = TokenType.TAG
        ret.append((token, token_type))
    return ret
