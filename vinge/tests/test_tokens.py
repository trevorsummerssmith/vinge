from vinge.tokens import *

class TestTokens:
    def test_is_uuid_id(self):
        id = "200d9d90-f544-11e1-a21f-0800200c9a66"
        assert is_token_id(id)

    def test_is_urn_id(self):
        id = "urn:okthen/blah:okthen/foo82i2-ak"
        assert is_token_id(id)

    def test_part_of_a_uuid_is_not_an_id(self):
        id = "200d9d90"
        assert not is_token_id(id)

    def test_foo_is_not_id(self):
        assert not is_token_id("foo")

    def test_tokenize_one_uuid(self):
        string = "368c6f60-f544-11e1-a21f-0800200c9a66"
        tokens = tokenize(string)
        assert tokens == [("368c6f60-f544-11e1-a21f-0800200c9a66", TokenType.ID)]

    def test_tokenize_one_uuid_with_two_words(self):
        string = "bar 439dc5a0-f544-11e1-a21f-0800200c9a66 888abklj"
        tokens = tokenize(string)
        assert tokens == [("bar", TokenType.TAG),
                          ("439dc5a0-f544-11e1-a21f-0800200c9a66", TokenType.ID),
                          ("888abklj", TokenType.TAG)]

    def test_tokenize_uuid_urn_words(self):
        string = "okthen urn:foo f93f3a70-f543-11e1-a21f-0800200c9a66 blarg"
        tokens = tokenize(string)
        assert tokens == [("okthen", TokenType.TAG),
                          ("urn:foo", TokenType.ID),
                          ("f93f3a70-f543-11e1-a21f-0800200c9a66", TokenType.ID),
                          ("blarg", TokenType.TAG)]

    def test_tokenize_skips_stop_word(self):
        tokens = tokenize("bar the it is foo")
        assert tokens == [("bar", TokenType.TAG), ("foo", TokenType.TAG)]

